from rest_framework import serializers
from concurrent.futures import ThreadPoolExecutor
from apps.article.models import Article, ArticleImage
import base64
from django.core.files.base import ContentFile

class ArticleImageSerializer(serializers.ModelSerializer):
    image = serializers.CharField()  # Base64 image input field
    pic_type = serializers.ChoiceField(choices=(("small", "Small"), ("large", "Large")))

    class Meta:
        model = ArticleImage
        fields = ['id', 'image', 'pic_type']

    def create(self, validated_data):
        image_data = validated_data.pop('image')
        # 解析 Base64 圖片數據
        format, imgstr = image_data.split(';base64,')
        ext = format.split('/')[-1]
        data = ContentFile(base64.b64decode(imgstr), name=f'temp.{ext}')
        return ArticleImage.objects.create(image=data, **validated_data)

class ArticleSerializer(serializers.ModelSerializer):
    images = ArticleImageSerializer(many=True, required=False)

    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'active', 'created_at', 'publish_at', 'expire_at', 'view_count', 'link', 'images']

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        article = Article.objects.create(**validated_data)

        # 使用 ThreadPoolExecutor 處理圖片上傳
        def process_image(image_data):
            ArticleImageSerializer().create({**image_data, 'article': article})

        with ThreadPoolExecutor(max_workers=5) as executor:  # 最多啟用 5 個執行緒
            for image_data in images_data:
                executor.submit(process_image, image_data)

        return article

    def update(self, instance, validated_data):
        images_data = validated_data.pop('images', [])

        # 更新文章內容
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.active = validated_data.get('active', instance.active)
        instance.publish_at = validated_data.get('publish_at', instance.publish_at)
        instance.expire_at = validated_data.get('expire_at', instance.expire_at)
        instance.view_count = validated_data.get('view_count', instance.view_count)
        instance.link = validated_data.get('link', instance.link)
        instance.save()

        # 獲取當前圖片的 ID 列表
        existing_image_ids = [img.id for img in instance.images.all()]

        # 刪除移除的圖片
        for img in instance.images.all():
            if img.id not in [img_data.get('id') for img_data in images_data]:
                img.delete()

        # 使用 ThreadPoolExecutor 處理圖片更新
        def process_image_update(image_data):
            image_id = image_data.get('id', None)
            if image_id and image_id in existing_image_ids:
                # 如果圖片已經存在，則更新該圖片
                image_instance = ArticleImage.objects.get(id=image_id)
                ArticleImageSerializer().update(image_instance, image_data)
            else:
                # 如果圖片不存在，則創建新圖片
                ArticleImageSerializer().create({**image_data, 'article': instance})

        with ThreadPoolExecutor(max_workers=5) as executor:
            for image_data in images_data:
                executor.submit(process_image_update, image_data)

        return instance

class ArticleSerializer_TableOutput(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'title', 'publish_at']
