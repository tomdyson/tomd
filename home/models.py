from django.db import models

from wagtail.models import Page


class HomePage(Page):
    pass

    def get_context(self, request):
        # Update context to include only published posts, 
        # in reverse chronological order
        context = super(HomePage, self).get_context(request)
        live_blogpages = self.get_children().live().filter(show_in_menus=False)
        context['blogpages'] = live_blogpages.order_by('-first_published_at')
        return context
