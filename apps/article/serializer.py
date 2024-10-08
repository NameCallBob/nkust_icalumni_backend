from rest_framework import serializers
from apps.article.models import Article, ArticleImage
import base64
from django.core.files.base import ContentFile

class ArticleImageSerializer(serializers.ModelSerializer):
    image = serializers.CharField()  # Base64 image input field
    pic_type = serializers.ChoiceField(choices=(("small", "Small"), ("large", "Large")))

    class Meta:
        model = ArticleImage
        fields = ['id', 'image', 'pic_type']

    # 保存 Base64 編碼的圖片
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

    # 新增或更新文章時，處理圖片數據
    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        article = Article.objects.create(**validated_data)

        # 創建與文章相關的圖片
        for image_data in images_data:
            ArticleImageSerializer().create({**image_data, 'article': article})

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

        # 清除現有圖片並重新創建圖片
        instance.images.all().delete()  # 清除舊圖片
        for image_data in images_data:
            ArticleImageSerializer().create({**image_data, 'article': instance})

        return instance

class ArticleSerializer_TableOutput(serializers.ModelSerializer):
        class Meta:
            model = Article
            fields = ['id', 'title', 'publish_at']
