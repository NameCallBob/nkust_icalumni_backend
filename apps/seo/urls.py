from django.urls import path
from .views import (
    DynamicSitemapView,
    SearchSEOView,
    RobotsTxtView
)

urlpatterns = [
    # Sitemap
    path('sitemap.xml', DynamicSitemapView.as_view(), name='dynamic-sitemap'),

    # SEO 資料端點
    path('search/', SearchSEOView.as_view(), name='search-seo'),

    # Robots.txt
    path('robots.txt', RobotsTxtView.as_view(), name='robots-txt'),
]