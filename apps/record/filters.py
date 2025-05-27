# monitoring/filters.py
import django_filters
from django.db.models import Q
from django_filters import rest_framework as filters
from .models import (RequestLog, QueryLog, PopularQuery, IPLimit, 
                     CRUDLog, ErrorLog, PerformanceMetric)


class RequestLogFilter(django_filters.FilterSet):
    """RequestLog 模型的過濾器"""
    # 時間範圍過濾
    start_date = django_filters.DateTimeFilter(field_name='timestamp', lookup_expr='gte')
    end_date = django_filters.DateTimeFilter(field_name='timestamp', lookup_expr='lte')
    
    # 路徑過濾
    path_contains = django_filters.CharFilter(field_name='path', lookup_expr='icontains')
    path_startswith = django_filters.CharFilter(field_name='path', lookup_expr='istartswith')
    
    # 處理時間範圍
    min_time = django_filters.NumberFilter(field_name='processing_time', lookup_expr='gte')
    max_time = django_filters.NumberFilter(field_name='processing_time', lookup_expr='lte')
    
    # 響應狀態碼範圍
    min_status = django_filters.NumberFilter(field_name='response_status', lookup_expr='gte')
    max_status = django_filters.NumberFilter(field_name='response_status', lookup_expr='lte')
    
    # 是否為API調用
    is_api = django_filters.BooleanFilter(field_name='is_api_call')
    
    # 使用自定義方法過濾請求內容
    request_body_contains = django_filters.CharFilter(method='filter_request_body')
    
    class Meta:
        model = RequestLog
        fields = {
            'user_id': ['exact'],
            'ip_address': ['exact', 'startswith'],
            'method': ['exact', 'in'],
            'response_status': ['exact', 'in'],
            'device_type': ['exact', 'in'],
            'country': ['exact', 'in'],
        }
        
    def filter_request_body(self, queryset, name, value):
        """過濾請求內容中包含特定字符串的記錄"""
        return queryset.filter(request_body__icontains=value)


class QueryLogFilter(django_filters.FilterSet):
    """QueryLog 模型的過濾器"""
    # 時間範圍過濾
    start_date = django_filters.DateTimeFilter(field_name='timestamp', lookup_expr='gte')
    end_date = django_filters.DateTimeFilter(field_name='timestamp', lookup_expr='lte')
    
    # 查詢內容過濾
    query_contains = django_filters.CharFilter(field_name='query', lookup_expr='icontains')
    
    # 處理時間範圍
    min_time = django_filters.NumberFilter(field_name='processing_time', lookup_expr='gte')
    max_time = django_filters.NumberFilter(field_name='processing_time', lookup_expr='lte')
    
    # 結果數量範圍
    min_results = django_filters.NumberFilter(field_name='results_count', lookup_expr='gte')
    max_results = django_filters.NumberFilter(field_name='results_count', lookup_expr='lte')
    
    class Meta:
        model = QueryLog
        fields = {
            'search_type': ['exact', 'in'],
            'device_type': ['exact', 'in'],
            'country': ['exact', 'in'],
            'hashed_ip': ['exact'],
        }


class PopularQueryFilter(django_filters.FilterSet):
    """PopularQuery 模型的過濾器"""
    # 查詢內容過濾
    query_contains = django_filters.CharFilter(field_name='query', lookup_expr='icontains')
    
    # 頻率範圍
    min_frequency = django_filters.NumberFilter(field_name='frequency', lookup_expr='gte')
    max_frequency = django_filters.NumberFilter(field_name='frequency', lookup_expr='lte')
    
    # 點擊次數範圍
    min_clicks = django_filters.NumberFilter(field_name='click_count', lookup_expr='gte')
    max_clicks = django_filters.NumberFilter(field_name='click_count', lookup_expr='lte')
    
    # 最後搜索時間範圍
    last_searched_after = django_filters.DateTimeFilter(field_name='last_searched', lookup_expr='gte')
    last_searched_before = django_filters.DateTimeFilter(field_name='last_searched', lookup_expr='lte')
    
    class Meta:
        model = PopularQuery
        fields = {
            'category': ['exact', 'in'],
        }


class IPLimitFilter(django_filters.FilterSet):
    """IPLimit 模型的過濾器"""
    # 請求次數範圍
    min_requests = django_filters.NumberFilter(field_name='request_count', lookup_expr='gte')
    max_requests = django_filters.NumberFilter(field_name='request_count', lookup_expr='lte')
    
    # 總請求次數範圍
    min_total_requests = django_filters.NumberFilter(field_name='total_request_count', lookup_expr='gte')
    max_total_requests = django_filters.NumberFilter(field_name='total_request_count', lookup_expr='lte')
    
    # 最後請求時間範圍
    last_request_after = django_filters.DateTimeFilter(field_name='last_request', lookup_expr='gte')
    last_request_before = django_filters.DateTimeFilter(field_name='last_request', lookup_expr='lte')
    
    # 封鎖至何時範圍
    block_until_after = django_filters.DateTimeFilter(field_name='block_until', lookup_expr='gte')
    block_until_before = django_filters.DateTimeFilter(field_name='block_until', lookup_expr='lte')
    
    # 封鎖原因過濾
    block_reason_contains = django_filters.CharFilter(field_name='block_reason', lookup_expr='icontains')
    
    class Meta:
        model = IPLimit
        fields = {
            'is_blocked': ['exact'],
            'hashed_ip': ['exact', 'startswith'],
        }


class CRUDLogFilter(django_filters.FilterSet):
    """CRUDLog 模型的過濾器"""
    # 時間範圍過濾
    start_date = django_filters.DateTimeFilter(field_name='timestamp', lookup_expr='gte')
    end_date = django_filters.DateTimeFilter(field_name='timestamp', lookup_expr='lte')
    
    # 應用和模型過濾
    app_model = django_filters.CharFilter(method='filter_app_model')
    
    # 資料快照過濾
    data_contains = django_filters.CharFilter(method='filter_data_snapshot')
    
    # 變更內容過濾
    changes_field = django_filters.CharFilter(method='filter_changes_field')
    
    class Meta:
        model = CRUDLog
        fields = {
            'user': ['exact'],
            'app_name': ['exact', 'in'],
            'model_name': ['exact', 'in'],
            'action_type': ['exact', 'in'],
            'object_id': ['exact'],
            'ip_address': ['exact', 'startswith'],
        }
    
    def filter_app_model(self, queryset, name, value):
        """過濾應用和模型結合 (app_name.model_name 格式)"""
        if '.' in value:
            app, model = value.split('.', 1)
            return queryset.filter(app_name=app, model_name=model)
        return queryset
    
    def filter_data_snapshot(self, queryset, name, value):
        """過濾資料快照中包含特定字符串的記錄"""
        return queryset.filter(data_snapshot__contains=value)
    
    def filter_changes_field(self, queryset, name, value):
        """過濾特定欄位的變更"""
        return queryset.filter(changes__has_key=value)


class ErrorLogFilter(django_filters.FilterSet):
    """ErrorLog 模型的過濾器"""
    # 時間範圍過濾
    start_date = django_filters.DateTimeFilter(field_name='timestamp', lookup_expr='gte')
    end_date = django_filters.DateTimeFilter(field_name='timestamp', lookup_expr='lte')
    
    # 訊息過濾
    message_contains = django_filters.CharFilter(field_name='message', lookup_expr='icontains')
    
    # 堆疊追蹤過濾
    traceback_contains = django_filters.CharFilter(field_name='traceback', lookup_expr='icontains')
    
    # 處理狀態複合過濾
    handled_status = django_filters.ChoiceFilter(
        choices=[
            ('all', '全部'),
            ('handled', '已處理'),
            ('unhandled', '未處理'),
        ],
        method='filter_handled_status',
        empty_label=None
    )
    
    # 處理時間範圍
    handled_after = django_filters.DateTimeFilter(field_name='handled_at', lookup_expr='gte')
    handled_before = django_filters.DateTimeFilter(field_name='handled_at', lookup_expr='lte')
    
    class Meta:
        model = ErrorLog
        fields = {
            'level': ['exact', 'in'],
            'handled': ['exact'],
            'handled_by': ['exact'],
            'request_log': ['exact'],
        }
    
    def filter_handled_status(self, queryset, name, value):
        """根據處理狀態過濾"""
        if value == 'handled':
            return queryset.filter(handled=True)
        elif value == 'unhandled':
            return queryset.filter(handled=False)
        return queryset


class PerformanceMetricFilter(django_filters.FilterSet):
    """PerformanceMetric 模型的過濾器"""
    # 時間範圍過濾
    start_date = django_filters.DateTimeFilter(field_name='timestamp', lookup_expr='gte')
    end_date = django_filters.DateTimeFilter(field_name='timestamp', lookup_expr='lte')
    
    # 指標值範圍
    min_value = django_filters.NumberFilter(field_name='value', lookup_expr='gte')
    max_value = django_filters.NumberFilter(field_name='value', lookup_expr='lte')
    
    # 指標名稱過濾
    name_contains = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    
    # 詳細資訊過濾
    details_contains = django_filters.CharFilter(method='filter_details_contains')
    
    class Meta:
        model = PerformanceMetric
        fields = {
            'metric_type': ['exact', 'in'],
            'name': ['exact', 'in'],
            'unit': ['exact', 'in'],
            'request_log': ['exact'],
        }
    
    def filter_details_contains(self, queryset, name, value):
        """過濾詳細資訊中包含特定字符串的記錄"""
        return queryset.filter(details__contains=value)


# 導出所有過濾器，方便在 views.py 中使用
__all__ = [
    'RequestLogFilter',
    'QueryLogFilter',
    'PopularQueryFilter',
    'IPLimitFilter',
    'CRUDLogFilter',
    'ErrorLogFilter',
    'PerformanceMetricFilter',
]