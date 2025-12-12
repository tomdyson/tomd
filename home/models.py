from django.db import models

from wagtail.models import Page


class HomePage(Page):
    pass

    def get_context(self, request):
        # Update context to include only published posts with show_in_menus=True,
        # in reverse chronological order by date
        from blog.models import BlogPage
        context = super(HomePage, self).get_context(request)
        # Get BlogPages that are descendants of this page with show_in_menus=True
        live_blogpages = BlogPage.objects.live().descendant_of(self).filter(show_in_menus=True)
        context['blogpages'] = live_blogpages.order_by('-date')
        return context
