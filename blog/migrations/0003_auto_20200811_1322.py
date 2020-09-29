# Generated by Django 3.0.7 on 2020-08-11 13:22

import blog.models
from django.db import migrations
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.embeds.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_auto_20180824_1250'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogpage',
            name='body',
            field=wagtail.core.fields.StreamField([('heading', wagtail.core.blocks.CharBlock(classname='full title', icon='title')), ('paragraph', wagtail.core.blocks.RichTextBlock(features=['bold', 'italic', 'link'], icon='pilcrow')), ('image', blog.models.ImageChooserBlock(icon='image')), ('embed', wagtail.embeds.blocks.EmbedBlock(icon='media'))]),
        ),
    ]