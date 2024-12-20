from rest_framework import serializers
from apps.article.models import Article, ArticleImage
import base64
from django.core.files.base import ContentFile
from asgiref.sync import sync_to_async
from django.db import transaction

class ArticleImageSerializer(serializers.ModelSerializer):
    image = serializers.CharField()  # Base64 image input field
    pic_type = serializers.ChoiceField(choices=(("small", "Small"), ("large", "Large")))

    class Meta:
        model = ArticleImage
        fields = ['id', 'image', 'pic_type']

    async def create(self, validated_data):
        image_data = validated_data.pop('image')
        # 解析 Base64 圖片數據
        format, imgstr = image_data.split(';base64,')
        ext = format.split('/')[-1]
        data = ContentFile(base64.b64decode(imgstr), name=f'temp.{ext}')
        return await ArticleImage.objects.acreate(image=data, **validated_data)

    async def update(self, instance, validated_data):
        image_data = validated_data.get('image', None)
        if image_data:
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name=f'temp.{ext}')
            instance.image = data

        instance.pic_type = validated_data.get('pic_type', instance.pic_type)
        await sync_to_async(instance.save)()
        return instance

class ArticleSerializer(serializers.ModelSerializer):
    images = ArticleImageSerializer(many=True, required=False)

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'content', 'active', 'created_at', 
            'publish_at', 'expire_at', 'view_count', 'link', 'images'
        ]

    async def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        async with transaction.atomic():
            article = await Article.objects.acreate(**validated_data)

            # 創建與文章相關的圖片
            for image_data in images_data:
                await ArticleImageSerializer().create({**image_data, 'article': article})

            return article

    async def update(self, instance, validated_data):
        images_data = validated_data.pop('images', [])

        # 更新文章內容
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.active = validated_data.get('active', instance.active)
        instance.publish_at = validated_data.get('publish_at', instance.publish_at)
        instance.expire_at = validated_data.get('expire_at', instance.expire_at)
        instance.view_count = validated_data.get('view_count', instance.view_count)
        instance.link = validated_data.get('link', instance.link)
        await sync_to_async(instance.save)()

        # 獲取當前圖片的ID列表
        existing_image_ids = [img.id for img in await instance.images.all()]

        # 刪除移除的圖片
        for img in await instance.images.all():
            if img.id not in [img_data.get('id') for img_data in images_data]:
                await sync_to_async(img.delete)()

        # 更新和新增圖片
        for image_data in images_data:
            image_id = image_data.get('id', None)
            if image_id and image_id in existing_image_ids:
                # 如果圖片已經存在，則更新該圖片
                image_instance = await ArticleImage.objects.aget(id=image_id)
                await ArticleImageSerializer().update(image_instance, image_data)
            else:
                # 如果圖片不存在，則創建新圖片
                await ArticleImageSerializer().create({**image_data, 'article': instance})

        return instance
class ArticleSerializer_TableOutput(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'title', 'publish_at']
