from django.db import models
from smartypants import smartypants
from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.images.blocks import ImageChooserBlock
from wagtail.embeds.blocks import EmbedBlock


class RichTextBlock(blocks.RichTextBlock):
    """Custom Rich Text Block with smartypants formatting"""

    def render(self, value, context=None):
        # Apply smartypants to convert quotes and dashes to smart equivalents
        html = super().render(value, context)
        clean = html.replace("&#x27;", "'").replace("&quot;", '"')
        return smartypants(clean)


class BlogPage(Page):
    date = models.DateField("Post date")
    body = StreamField(
        [
            ("heading", blocks.CharBlock(classname="full title", icon="title")),
            (
                "paragraph",
                RichTextBlock(icon="pilcrow", features=["bold", "italic", "link"]),
            ),
            ("image", ImageChooserBlock(icon="image")),
            ("embed", EmbedBlock(icon="media")),
        ],
        use_json_field=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel("date"),
        FieldPanel("body"),
    ]
