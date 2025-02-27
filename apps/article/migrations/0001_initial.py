# Generated by Django 5.0.2 on 2024-12-21 15:12

import ckeditor.fields
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('content', ckeditor.fields.RichTextField()),
                ('active', models.BooleanField(verbose_name='是否公開')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('publish_at', models.DateTimeField(blank=True, null=True, verbose_name='發布時間')),
                ('expire_at', models.DateTimeField(blank=True, null=True, verbose_name='截止時間')),
                ('view_count', models.PositiveIntegerField(default=0, verbose_name='查看次數')),
                ('link', models.URLField(blank=True, max_length=500, null=True, verbose_name='文章連結')),
            ],
        ),
        migrations.CreateModel(
            name='ArticleImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='static/article/')),
                ('pic_type', models.CharField(choices=[('small', '小圖'), ('large', '大圖')], default='small', max_length=5, verbose_name='圖片大小')),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='article.article')),
            ],
        ),
    ]
