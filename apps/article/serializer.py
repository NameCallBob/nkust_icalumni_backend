from rest_framework import serializers
from concurrent.futures import ThreadPoolExecutor
from apps.article.models import Article, ArticleImage
from apps.deal_base64 import Base64ImageField

class ArticleImageSerializer(serializers.ModelSerializer):
    # ModelSerializer 預設把 PK 設為 read_only，會讓 ArticleSerializer.update() 用來比對
    # 「更新既有圖片 vs 新增圖片」的 id 永遠讀不到（validated_data 會被剝除），
    # 導致每次編輯都誤刪既有圖片、新增出沒有檔案的空白列。這裡明確宣告成非唯讀以修正。
    id = serializers.IntegerField(required=False)
    image = Base64ImageField(required=False, allow_null=True)
    pic_type = serializers.ChoiceField(choices=(("small", "Small"), ("large", "Large")))

    class Meta:
        model = ArticleImage
        fields = ['id', 'image', 'pic_type', 'priority']

    def create(self, validated_data):
        # id 只用於在 ArticleSerializer.update() 比對「更新既有圖片 vs 新增圖片」，
        # 新建時絕不可讓呼叫端指定 PK（否則可能撞號或讓資料庫指派其他文章既有的 id）。
        validated_data.pop('id', None)
        # image 已由 Base64ImageField.to_internal_value 驗證/壓縮成 WebP，直接使用即可
        return ArticleImage.objects.create(**validated_data)

    def update(self, instance, validated_data):
        image = validated_data.pop('image', None)
        if image:
            instance.image = image
        instance.pic_type = validated_data.get('pic_type', instance.pic_type)
        instance.save()
        return instance


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
