from rest_framework import serializers
from apps.picture.models import PromotionAd,ContinuousAd,OtherImage

class PromotionAdSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromotionAd
        fields = '__all__'

class ContinuousAdSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContinuousAd
        fields = '__all__'

class OtherImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = OtherImage
        fields = '__all__'
