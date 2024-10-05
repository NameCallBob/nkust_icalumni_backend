from rest_framework import serializers
from apps.company.models import Company , Industry

class IndustrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = ['id', 'title', 'intro']  # 包含所有需要的欄位

class CompanySerializer(serializers.ModelSerializer):
    industry = IndustrySerializer()  # 嵌套 IndustrySerializer 顯示完整的行業資訊

    class Meta:
        model = Company
        fields = [
            'id', 'name', 'member', 'industry', 'positions', 'description',
            'products', 'product_description', 'photo', 'website',
            'address', 'email', 'phone_number'
        ]  # 包含所有的欄位

    def create(self, validated_data):
        # 分離出 industry 的資料
        industry_data = validated_data.pop('industry')
        # 確認是否需要創建或取得已存在的行業
        industry, created = Industry.objects.get_or_create(**industry_data)
        # 建立公司
        company = Company.objects.create(industry=industry, **validated_data)
        return company

    def update(self, instance, validated_data):
        # 處理 industry 的修改
        industry_data = validated_data.get('industry', None)
        if industry_data:
            # 確認是否需要創建或取得已存在的行業
            industry, created = Industry.objects.get_or_create(**industry_data)
            instance.industry = industry

        # 逐步處理其他欄位，使用 get 方法來支援部分更新
        instance.name = validated_data.get('name', instance.name)
        instance.positions = validated_data.get('positions', instance.positions)
        instance.description = validated_data.get('description', instance.description)
        instance.products = validated_data.get('products', instance.products)
        instance.product_description = validated_data.get('product_description', instance.product_description)
        instance.photo = validated_data.get('photo', instance.photo)
        instance.website = validated_data.get('website', instance.website)
        instance.address = validated_data.get('address', instance.address)
        instance.email = validated_data.get('email', instance.email)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)

        # 保存修改
        instance.save()
        return instance
