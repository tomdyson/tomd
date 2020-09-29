from django.db import models
from wagtail.core.models import Page
from wagtail.core.fields import StreamField
from wagtail.core import blocks
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.api import APIField
from wagtail.images.blocks import ImageChooserBlock as DefaultImageChooserBlock
from wagtail.embeds.blocks import EmbedBlock as DefaultEmbedBlock
from wagtail.embeds.embeds import get_embed


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


class BlogPage(Page):
    date = models.DateField("Post date")
    body = StreamField(
        [
            ("heading", blocks.CharBlock(classname="full title", icon="title")),
            (
                "paragraph",
                blocks.RichTextBlock(
                    icon="pilcrow", features=["bold", "italic", "link"]
                ),
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

