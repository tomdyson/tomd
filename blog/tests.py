from django.test import TestCase, Client
from django.contrib.auth.models import User
from wagtail.models import Page, Site
from wagtail.test.utils import WagtailPageTestCase
from home.models import HomePage
from blog.models import BlogPage
import json


class BlogPageTests(WagtailPageTestCase):
    """Test the BlogPage model"""

    def setUp(self):
        """Set up test data"""
        self.root_page = Page.get_first_root_node()
        self.home_page = HomePage(title="Test Home", slug="test-home")
        self.root_page.add_child(instance=self.home_page)

        self.blog_page = BlogPage(
            title="Test Blog Post",
            slug="test-blog-post",
            date="2024-01-01",
            body=[
                {"type": "heading", "value": "Test Heading"},
                {"type": "paragraph", "value": "<p>Test paragraph with <b>bold</b> text</p>"},
            ],
        )
        self.home_page.add_child(instance=self.blog_page)

    def test_can_create_blog_page(self):
        """Test that a blog page can be created"""
        self.assertIsInstance(self.blog_page, BlogPage)
        self.assertEqual(self.blog_page.title, "Test Blog Post")

    def test_blog_page_parent(self):
        """Test that blog pages can be children of HomePage"""
        self.assertCanCreateAt(HomePage, BlogPage)

    def test_blog_page_has_date(self):
        """Test that blog page has a date field"""
        self.assertEqual(str(self.blog_page.date), "2024-01-01")

    def test_blog_page_streamfield(self):
        """Test that blog page has StreamField body"""
        self.assertEqual(len(self.blog_page.body), 2)
        self.assertEqual(self.blog_page.body[0].block_type, "heading")
        self.assertEqual(self.blog_page.body[1].block_type, "paragraph")


class HeadlessAPITests(TestCase):
    """Test the headless API endpoints"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()

        # Get or create site
        if Site.objects.filter(is_default_site=True).exists():
            self.site = Site.objects.get(is_default_site=True)
        else:
            root = Page.get_first_root_node()
            self.site = Site.objects.create(
                hostname='localhost',
                root_page=root,
                is_default_site=True
            )

        # Get root page
        self.root_page = Page.get_first_root_node()

        # Create home page with unique slug
        import time
        unique_suffix = str(int(time.time() * 1000000))
        self.home_page = HomePage(title="Home", slug=f"home-{unique_suffix}")
        self.root_page.add_child(instance=self.home_page)
        self.site.root_page = self.home_page
        self.site.save()

        # Create blog pages
        self.blog_page_1 = BlogPage(
            title="First Blog Post",
            slug="first-post",
            date="2024-01-01",
            body=[
                {"type": "heading", "value": "First Heading"},
                {"type": "paragraph", "value": "<p>First paragraph</p>"},
            ],
        )
        self.home_page.add_child(instance=self.blog_page_1)
        self.blog_page_1.save_revision().publish()

        self.blog_page_2 = BlogPage(
            title="Second Blog Post",
            slug="second-post",
            date="2024-01-02",
            body=[
                {"type": "heading", "value": "Second Heading"},
                {"type": "paragraph", "value": "<p>Second paragraph</p>"},
            ],
        )
        self.home_page.add_child(instance=self.blog_page_2)
        self.blog_page_2.save_revision().publish()

    def test_api_pages_listing(self):
        """Test that the API pages listing endpoint works"""
        response = self.client.get("/api/v2/pages/")
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertIn("items", data)
        self.assertIn("meta", data)

        # Should have at least our test pages
        self.assertGreaterEqual(len(data["items"]), 2)

    def test_api_page_detail_by_id(self):
        """Test that the API page detail endpoint works with ID"""
        response = self.client.get(f"/api/v2/pages/{self.blog_page_1.id}/")
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertEqual(data["title"], "First Blog Post")
        self.assertIn("body", data)
        self.assertIn("date", data)

    def test_api_page_detail_by_slug(self):
        """Test that the API page detail endpoint works with slug"""
        response = self.client.get(f"/api/v2/pages/{self.blog_page_1.slug}/")
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertEqual(data["title"], "First Blog Post")

    def test_api_blog_page_body_structure(self):
        """Test that the blog page body is correctly serialized in the API"""
        response = self.client.get(f"/api/v2/pages/{self.blog_page_1.id}/")
        data = json.loads(response.content)

        self.assertIn("body", data)
        body = data["body"]

        # Check that body is a list
        self.assertIsInstance(body, list)
        self.assertEqual(len(body), 2)

        # Check heading block
        heading = body[0]
        self.assertEqual(heading["type"], "heading")
        self.assertIn("value", heading)

        # Check paragraph block
        paragraph = body[1]
        self.assertEqual(paragraph["type"], "paragraph")
        self.assertIn("value", paragraph)

    def test_api_published_vs_draft(self):
        """Test published vs draft page status"""
        # Create a published page
        published_page = BlogPage(
            title="Published Post",
            slug="published-post",
            date="2024-01-03",
            body=[
                {"type": "heading", "value": "Published Heading"},
            ],
        )
        self.home_page.add_child(instance=published_page)
        published_page.save_revision().publish()

        # Create a draft page
        draft_page = BlogPage(
            title="Draft Post",
            slug="draft-post",
            date="2024-01-04",
            body=[
                {"type": "heading", "value": "Draft Heading"},
            ],
        )
        self.home_page.add_child(instance=draft_page)
        # Save but don't publish
        draft_page.save_revision()
        draft_page.live = False
        draft_page.save()

        # Verify published page is accessible via API
        response = self.client.get(f"/api/v2/pages/{published_page.id}/")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["title"], "Published Post")

        # Verify draft (non-live) page is NOT accessible via public API
        # This is the correct behavior for a headless CMS - only published content should be public
        response = self.client.get(f"/api/v2/pages/{draft_page.id}/")
        self.assertEqual(response.status_code, 404)

    def test_api_filtering_by_type(self):
        """Test that the API can filter pages by type"""
        response = self.client.get("/api/v2/pages/?type=blog.BlogPage")
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        # All returned items should be BlogPage
        for item in data["items"]:
            self.assertEqual(item["meta"]["type"], "blog.BlogPage")

    def test_api_date_field_in_response(self):
        """Test that blog page date is included in API response"""
        response = self.client.get(f"/api/v2/pages/{self.blog_page_1.id}/")
        data = json.loads(response.content)

        self.assertIn("date", data)
        self.assertEqual(data["date"], "2024-01-01")


class ImageChooserBlockTests(TestCase):
    """Test the custom ImageChooserBlock API representation"""

    def setUp(self):
        """Set up test data"""
        import time
        unique_suffix = str(int(time.time() * 1000000))
        self.root_page = Page.get_first_root_node()
        self.home_page = HomePage(title="Home", slug=f"home-{unique_suffix}")
        self.root_page.add_child(instance=self.home_page)

    def test_image_block_api_representation(self):
        """Test that ImageChooserBlock has correct API representation"""
        from blog.models import ImageChooserBlock
        from wagtail.images.tests.utils import get_test_image_file
        from wagtail.images.models import Image

        # Create a test image
        test_image = Image.objects.create(
            title="Test Image",
            file=get_test_image_file(),
        )

        # Create a block and get its API representation
        block = ImageChooserBlock()
        api_repr = block.get_api_representation(test_image)

        self.assertIsNotNone(api_repr)
        self.assertIn("id", api_repr)
        self.assertIn("title", api_repr)
        self.assertIn("original", api_repr)
        self.assertIn("medium", api_repr)


class RichTextBlockTests(TestCase):
    """Test the custom RichTextBlock with smartypants"""

    def test_richtext_block_smartypants(self):
        """Test that RichTextBlock applies smartypants formatting"""
        from blog.models import RichTextBlock

        block = RichTextBlock()

        # Test with quotes
        input_text = '<p>This is a "test" with \'quotes\'</p>'
        # The clean_and_smarten method should convert quotes to smart quotes
        cleaned = block.clean_and_smarten('This is a "test" with \'quotes\'')

        # Smartypants should convert straight quotes to curly quotes
        self.assertNotEqual(cleaned, 'This is a "test" with \'quotes\'')


class HomePageTests(WagtailPageTestCase):
    """Test the HomePage model"""

    def test_can_create_home_page(self):
        """Test that a home page can be created"""
        root_page = Page.get_first_root_node()
        home_page = HomePage(title="Test Home", slug="test-home")
        root_page.add_child(instance=home_page)

        self.assertIsInstance(home_page, HomePage)

    def test_home_page_children(self):
        """Test that home page can have blog page children"""
        self.assertCanCreateAt(HomePage, BlogPage)
