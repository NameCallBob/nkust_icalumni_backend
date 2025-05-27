from django.contrib import admin
from apps.article.models import Article,ArticleImage

admin.site.register(Article)
admin.site.register(ArticleImage)