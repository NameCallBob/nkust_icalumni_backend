from rest_framework import serializers
from apps.recruit.models import Recruit

class RecruitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recruit
        fields = ['id', 'company', 'title', 'intro', 'click', 'deadline', 'release_date','active']

class RecruitSerializer_forTable(serializers.ModelSerializer):
    class Meta:
        model = Recruit
        fields = ['id', 'company', 'title', 'deadline']
