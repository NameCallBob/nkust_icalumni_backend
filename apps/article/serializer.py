from rest_framework import serializers
from apps.article.models import Article, ArticleImage

class ArticleImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleImage
        fields = ['image']

class ArticleSerializer(serializers.ModelSerializer):
    images = ArticleImageSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'created_at', 'images']

class ArticleCreateSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(), write_only=True
    )

    class Meta:
        model = Article
        fields = ['title', 'content', 'images']

    def create(self, validated_data):
        images = validated_data.pop('images')
        article = Article.objects.create(**validated_data)
        for image in images:
            ArticleImage.objects.create(article=article, image=image)
        return article
