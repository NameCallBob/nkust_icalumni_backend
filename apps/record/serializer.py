# monitoring/serializers.py
from rest_framework import serializers
from apps.record.models import (RequestLog, QueryLog, PopularQuery, IPLimit, 
                     CRUDLog, ErrorLog, PerformanceMetric)


class RequestLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestLog
        fields = '__all__'


class QueryLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = QueryLog
        fields = '__all__'


class PopularQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = PopularQuery
        fields = '__all__'


class IPLimitSerializer(serializers.ModelSerializer):
    class Meta:
        model = IPLimit
        fields = '__all__'


class CRUDLogSerializer(serializers.ModelSerializer):
    user_display = serializers.SerializerMethodField()
    
    class Meta:
        model = CRUDLog
        fields = '__all__'
        
    def get_user_display(self, obj):
        if obj.user:
            return obj.user.username
        return "匿名"


class ErrorLogSerializer(serializers.ModelSerializer):
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    
    class Meta:
        model = ErrorLog
        fields = '__all__'


class PerformanceMetricSerializer(serializers.ModelSerializer):
    metric_type_display = serializers.CharField(source='get_metric_type_display', read_only=True)
    
    class Meta:
        model = PerformanceMetric
        fields = '__all__'

from apps.record.models import ContactMessage

class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ['id', 'name', 'email', 'phone', 'message', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_message(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("訊息內容不可為空")
        if len(value) > 5000:
            raise serializers.ValidationError("訊息內容過長（上限 5000 字）")
        return value

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("姓名不可為空")
        return value
