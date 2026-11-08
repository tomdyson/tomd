import shutil
import tempfile
from datetime import date

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase, override_settings
from wagtail.embeds.embeds import get_embed_hash
from wagtail.embeds.models import Embed
from wagtail.images.models import Image
from wagtail.images.tests.utils import get_test_image_file
from wagtail.models import Page
from wagtail.rich_text import RichText

from blog.models import BlogPage, RichTextBlock
from home.models import HomePage

MEDIA_ROOT = tempfile.mkdtemp()
EMBED_URL = "https://www.youtube.com/watch?v=test"


def tearDownModule():
    shutil.rmtree(MEDIA_ROOT, ignore_errors=True)


# The manifest storage in the real settings needs collectstatic to have run
@override_settings(
    MEDIA_ROOT=MEDIA_ROOT,
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    },
)
class SiteTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # The homepage and default site come from home's migrations
        cls.home = HomePage.objects.get()
        # Stored so that rendering the page doesn't call out to YouTube
        Embed.objects.create(
            url=EMBED_URL,
            hash=get_embed_hash(EMBED_URL),
            type="video",
            html="<iframe title='test embed'></iframe>",
        )
        image = Image.objects.create(title="Test", file=get_test_image_file())
        cls.post = cls.home.add_child(
            instance=BlogPage(
                title="A post",
                slug="a-post",
                date=date(2026, 1, 1),
                show_in_menus=True,
                body=[
                    ("heading", "A heading"),
                    ("paragraph", RichText('<p>Some "quoted" text</p>')),
                    ("image", image),
                    ("embed", EMBED_URL),
                ],
            )
        )
        cls.about = cls.home.add_child(
            instance=BlogPage(
                title="About",
                slug="about",
                date=date(2026, 1, 2),
                body=[("heading", "About me")],
            )
        )


class PublicSiteTests(SiteTestCase):
    def test_every_live_page_returns_200(self):
        pages = Page.objects.live().filter(depth__gt=1).specific()
        self.assertEqual(pages.count(), 3)
        for page in pages:
            with self.subTest(url=page.url):
                self.assertEqual(self.client.get(page.url).status_code, 200)

    def test_homepage_lists_posts_shown_in_menus(self):
        response = self.client.get("/")
        self.assertContains(response, "A post")
        self.assertNotContains(response, "About me")

    def test_blog_page_renders_every_block_type(self):
        response = self.client.get("/a-post/")
        self.assertContains(response, "A heading")
        self.assertContains(response, "<p>Some &#8220;quoted&#8221; text</p>")
        self.assertContains(response, "<img")
        self.assertContains(response, "test embed")

    def test_unknown_page_renders_404_template(self):
        response = self.client.get("/no-such-page/")
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "404.html")

    def test_x_redirects_to_s3(self):
        response = self.client.get("/x/some/file.pdf")
        self.assertRedirects(
            response,
            "https://tom.s3.amazonaws.com/share/some/file.pdf",
            status_code=301,
            fetch_redirect_response=False,
        )


class RichTextBlockTests(SimpleTestCase):
    def test_render_applies_smart_quotes(self):
        html = RichTextBlock().render(RichText('<p>Some "quoted" text</p>'))
        self.assertIn("&#8220;quoted&#8221;", html)

    def test_render_converts_quote_entities_but_not_in_links(self):
        html = RichTextBlock().render(
            RichText('<p><a href="/?q=&quot;x&quot;">&quot;quoted&quot;</a></p>')
        )
        self.assertIn('<a href="/?q=&quot;x&quot;">', html)
        self.assertIn("&#8220;quoted&#8221;", html)


class AdminTests(SiteTestCase):
    def setUp(self):
        users = get_user_model().objects
        admin = users.create_superuser("admin", password="password")
        self.client.force_login(admin)

    def test_dashboard_loads(self):
        self.assertEqual(self.client.get("/admin/").status_code, 200)

    def test_blog_page_edit_view_loads(self):
        response = self.client.get(f"/admin/pages/{self.post.pk}/edit/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A post")
