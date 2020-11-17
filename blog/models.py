from django.db import models
from smartypants import smartypants
from wagtail.core.models import Page
from wagtail.core.fields import StreamField
from wagtail.core import blocks
from wagtail.core.templatetags.wagtailcore_tags import richtext
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.api import APIField
from wagtail.images.blocks import ImageChooserBlock as DefaultImageChooserBlock
from wagtail.embeds.blocks import EmbedBlock as DefaultEmbedBlock
from wagtail.embeds.embeds import get_embed
from wagtail_headless_preview.models import HeadlessPreviewMixin


class ImageChooserBlock(DefaultImageChooserBlock):
    # https://hodovi.cc/blog/recipes-when-building-headless-cms-wagtails-api/
    def get_api_representation(self, value, context=None):
        if value:
            original = value.get_rendition("original").attrs_dict
            width = 1600 if original["width"] > original["height"] else 1200
            return {
                "id": value.id,
                "title": value.title,
                "original": original,
                "medium": value.get_rendition(f"width-{width}").attrs_dict,
            }


class EmbedBlock(DefaultEmbedBlock):
    def get_api_representation(self, value, context=None):
        if value:
            embed = get_embed(value.url, max_width=612)
            return {"url": value.url, "html": embed.html}


class RichTextBlock(blocks.RichTextBlock):
    """Custom Rich Text Block returning HTML as its API representation"""

    def clean_and_smarten(self, str):
        #  replace HTML quotes and double quotes with ASCII equivalents,
        # then convert these to smart HTML quotes
        clean = str.replace("&#x27;", "'").replace("&quot;", '"')
        return smartypants(clean)

    def get_api_representation(self, value, context=None):
        # convert internal rich text format to HTML
        return richtext(self.clean_and_smarten(value.source))


class BlogPage(HeadlessPreviewMixin, Page):
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
        ]
    )

    content_panels = Page.content_panels + [
        FieldPanel("date"),
        StreamFieldPanel("body"),
    ]

    api_fields = [APIField("date"), APIField("body")]

