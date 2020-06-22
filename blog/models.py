from django.db import models
from wagtail.core.models import Page
from wagtail.core.fields import StreamField
from wagtail.core import blocks
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.api import APIField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.embeds.blocks import EmbedBlock


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

