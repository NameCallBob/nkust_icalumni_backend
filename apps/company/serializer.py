from rest_framework import serializers
from apps.company.models import Company , Industry

class IndustrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = ['id', 'title', 'intro']  # 包含所有需要的欄位

class CompanySerializer(serializers.ModelSerializer):
    industry = serializers.PrimaryKeyRelatedField(queryset=Industry.objects.all())  # 使用主鍵來關聯行業

    class Meta:
        model = Company
        fields = [
            'id', 'name', 'member', 'industry', 'positions', 'description',
            'products', 'product_description', 'photo', 'website',
            'address', 'email', 'phone_number'
        ]

    def create(self, validated_data):
        # industry 已經是通過 ID 關聯，因此可以直接使用
        industry = validated_data.pop('industry')
        # 建立公司
        company = Company.objects.create(industry=industry, **validated_data)
        return company

    def update(self, instance, validated_data):
        # 處理 industry 的修改
        industry = validated_data.get('industry', None)
        if industry:
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
