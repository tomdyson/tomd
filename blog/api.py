from django.urls import path

from wagtail.api.v2.views import PagesAPIViewSet
from wagtail.api.v2.router import WagtailAPIRouter


class CustomAPIEndpoint(PagesAPIViewSet):
    """
    Custom Pages API endpoint that allows finding pages by pk or slug
    https://dev.to/wagtail/wagtail-api-how-to-customize-the-detail-url-2j3l
    """

    def detail_view(self, request, pk=None, slug=None):
        param = pk
        if slug is not None:
            self.lookup_field = "slug"
            param = slug
        return super().detail_view(request, param)

    @classmethod
    def get_urlpatterns(cls):
        """
        This returns a list of URL patterns for the endpoint
        """
        return [
            path("", cls.as_view({"get": "listing_view"}), name="listing"),
            path("<int:pk>/", cls.as_view({"get": "detail_view"}), name="detail"),
            path("<slug:slug>/", cls.as_view({"get": "detail_view"}), name="detail"),
            path("find/", cls.as_view({"get": "find_view"}), name="find"),
        ]


api_router = WagtailAPIRouter("wagtailapi")
api_router.register_endpoint("pages", CustomAPIEndpoint)
