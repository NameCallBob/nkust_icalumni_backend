from django.db import models
from ckeditor.fields import RichTextField

class Article(models.Model):
    title = models.CharField(max_length=200)
    content = RichTextField()  # 支援 HTML
    active = models.BooleanField("是否公開")
    created_at = models.DateTimeField(auto_now_add=True)
    publish_at = models.DateTimeField("發布時間", null=True, blank=True)
    expire_at = models.DateTimeField("截止時間", null=True, blank=True)
    view_count = models.PositiveIntegerField("查看次數", default=0)
    link = models.URLField("文章連結", max_length=500, null=True, blank=True)

    def __str__(self):
        return self.title

class ArticleImage(models.Model):
    IMAGE_SIZE_CHOICES = [
        ('small', '小圖'),
        ('large', '大圖'),
    ]

    article = models.ForeignKey(Article, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='static/article/')
    pic_type = models.CharField("圖片大小", max_length=5, choices=IMAGE_SIZE_CHOICES, default='small')

    def __str__(self):
        return f"Image for {self.article.title}"
