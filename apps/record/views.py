# monitoring/views.py
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Avg, Min, Max, Sum

from apps.record.models import (RequestLog, QueryLog, PopularQuery, IPLimit, 
                     CRUDLog, ErrorLog, PerformanceMetric)
from apps.record.serializer import (RequestLogSerializer, QueryLogSerializer, 
                          PopularQuerySerializer, IPLimitSerializer, 
                          CRUDLogSerializer, ErrorLogSerializer,
                          PerformanceMetricSerializer)
from .filters import (RequestLogFilter, QueryLogFilter, CRUDLogFilter, 
                      ErrorLogFilter, PerformanceMetricFilter)


class RequestLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API 端點用於查詢請求日誌
    """
    queryset = RequestLog.objects.all().order_by('-timestamp')
    serializer_class = RequestLogSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = RequestLogFilter
    search_fields = ['path', 'user_agent', 'referer', 'ip_address', 'user_id']
    ordering_fields = ['timestamp', 'processing_time', 'response_status']
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """獲取請求統計資料"""
        # 時間範圍過濾
        days = int(request.query_params.get('days', 7))
        start_date = timezone.now() - timedelta(days=days)
        
        # 基礎查詢集
        queryset = RequestLog.objects.filter(timestamp__gte=start_date)
        
        # 計算統計資料
        stats = {
            'total_requests': queryset.count(),
            'average_time': queryset.aggregate(avg_time=Avg('processing_time'))['avg_time'],
            'by_status': queryset.values('response_status').annotate(count=Count('id')).order_by('-count'),
            'by_method': queryset.values('method').annotate(count=Count('id')).order_by('-count'),
            'by_path': queryset.values('path').annotate(
                count=Count('id'),
                avg_time=Avg('processing_time')
            ).order_by('-count')[:10],
            'by_device': queryset.values('device_type').annotate(count=Count('id')).order_by('-count'),
            'by_country': queryset.values('country').annotate(count=Count('id')).order_by('-count')[:10],
        }
        
        return Response(stats)


class QueryLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API 端點用於查詢使用者搜索記錄
    """
    queryset = QueryLog.objects.all().order_by('-timestamp')
    serializer_class = QueryLogSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = QueryLogFilter
    search_fields = ['query', 'search_type']
    ordering_fields = ['timestamp', 'processing_time']
    
    @action(detail=False, methods=['get'])
    def popular_terms(self, request):
        """獲取熱門搜索詞"""
        days = int(request.query_params.get('days', 30))
        limit = int(request.query_params.get('limit', 20))
        start_date = timezone.now() - timedelta(days=days)
        
        popular_terms = QueryLog.objects.filter(
            timestamp__gte=start_date
        ).values('query').annotate(
            count=Count('id')
        ).order_by('-count')[:limit]
        
        return Response(popular_terms)


class PopularQueryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API 端點用於查詢熱門搜索統計
    """
    queryset = PopularQuery.objects.all().order_by('-frequency')
    serializer_class = PopularQuerySerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category']
    search_fields = ['query']
    ordering_fields = ['frequency', 'click_count', 'last_searched']


class IPLimitViewSet(viewsets.ModelViewSet):
    """
    API 端點用於管理 IP 限制
    """
    queryset = IPLimit.objects.all().order_by('-last_request')
    serializer_class = IPLimitSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['is_blocked']
    ordering_fields = ['last_request', 'request_count', 'total_request_count']
    
    @action(detail=True, methods=['post'])
    def block(self, request, pk=None):
        """封鎖指定 IP"""
        ip_limit = self.get_object()
        reason = request.data.get('reason', '手動封鎖')
        hours = int(request.data.get('hours', 24))
        
        ip_limit.is_blocked = True
        ip_limit.block_reason = reason
        ip_limit.block_until = timezone.now() + timedelta(hours=hours)
        ip_limit.save()
        
        return Response({'status': 'success', 'message': f'IP已被封鎖 {hours} 小時'})
    
    @action(detail=True, methods=['post'])
    def unblock(self, request, pk=None):
        """解除封鎖指定 IP"""
        ip_limit = self.get_object()
        
        ip_limit.is_blocked = False
        ip_limit.block_until = None
        ip_limit.save()
        
        return Response({'status': 'success', 'message': 'IP封鎖已解除'})


class CRUDLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API 端點用於查詢 CRUD 操作日誌
    """
    queryset = CRUDLog.objects.all().order_by('-timestamp')
    serializer_class = CRUDLogSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = CRUDLogFilter
    search_fields = ['model_name', 'app_name', 'object_id']
    ordering_fields = ['timestamp', 'action_type']


class ErrorLogViewSet(viewsets.ModelViewSet):
    """
    API 端點用於管理錯誤日誌
    """
    queryset = ErrorLog.objects.all().order_by('-timestamp')
    serializer_class = ErrorLogSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ErrorLogFilter
    search_fields = ['message', 'traceback']
    ordering_fields = ['timestamp', 'level']
    
    @action(detail=True, methods=['post'])
    def mark_handled(self, request, pk=None):
        """標記錯誤為已處理"""
        error_log = self.get_object()
        error_log.handled = True
        error_log.handled_by = request.user
        error_log.handled_at = timezone.now()
        error_log.save()
        
        return Response({'status': 'success', 'message': '錯誤已標記為已處理'})


class PerformanceMetricViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API 端點用於查詢性能指標
    """
    queryset = PerformanceMetric.objects.all().order_by('-timestamp')
    serializer_class = PerformanceMetricSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = PerformanceMetricFilter
    ordering_fields = ['timestamp', 'value']
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """獲取性能統計資料"""
        days = int(request.query_params.get('days', 7))
        start_date = timezone.now() - timedelta(days=days)
        
        # 基礎查詢集
        queryset = PerformanceMetric.objects.filter(timestamp__gte=start_date)
        
        # 計算統計資料
        stats = {
            'by_metric_type': queryset.values('metric_type').annotate(
                count=Count('id'),
                avg_value=Avg('value'),
                min_value=Min('value'),
                max_value=Max('value'),
            ).order_by('metric_type'),
            
            'by_name': queryset.values('name').annotate(
                count=Count('id'),
                avg_value=Avg('value'),
                min_value=Min('value'),
                max_value=Max('value'),
            ).order_by('-avg_value')[:10],
        }
        
        return Response(stats)