# monitoring/models.py
from django.db import models
import uuid
import hashlib
from django.contrib.auth import get_user_model

User = get_user_model()

def uuid4_hex():
    """Generate UUID without hyphens (32 chars)"""
    return uuid.uuid4().hex

class RequestLog(models.Model):
    """使用者請求日誌模型"""
    id = models.CharField(primary_key=True, default=uuid4_hex, max_length=32, editable=False)
    user_id = models.CharField(max_length=100, null=True, blank=True, help_text="使用者ID或匿名標識")
    ip_address = models.GenericIPAddressField(help_text="請求IP地址")
    method = models.CharField(max_length=10, help_text="HTTP方法")
    path = models.CharField(max_length=255, help_text="請求路徑")
    query_params = models.TextField(null=True, blank=True, help_text="查詢參數")
    request_body = models.TextField(null=True, blank=True, help_text="請求內容")
    response_status = models.IntegerField(help_text="響應狀態碼")
    response_size = models.IntegerField(null=True, blank=True, help_text="響應大小(bytes)")
    processing_time = models.FloatField(help_text="處理時間(ms)")
    user_agent = models.TextField(null=True, blank=True, help_text="用戶代理字符串")
    referer = models.TextField(null=True, blank=True, help_text="來源頁面")
    timestamp = models.DateTimeField(auto_now_add=True, help_text="請求時間")
    # 新增欄位
    device_type = models.CharField(max_length=50, blank=True, null=True, help_text="設備類型")
    country = models.CharField(max_length=100, blank=True, null=True, help_text="IP來源國家")
    is_api_call = models.BooleanField(default=False, help_text="是否為API調用")
    user_session = models.CharField(max_length=100, blank=True, null=True, help_text="用戶會話ID")
    
    class Meta:
        db_table = 'request_logs'
        indexes = [
            models.Index(fields=['user_id']),
            models.Index(fields=['ip_address']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['path']),
        ]
        
    def __str__(self):
        return f"{self.method} {self.path} ({self.timestamp})"


class QueryLog(models.Model):
    """使用者查詢記錄"""
    query = models.TextField(help_text="使用者查詢內容", null=True)
    timestamp = models.DateTimeField(auto_now_add=True, help_text="查詢的時間")
    search_type = models.CharField(max_length=50, blank=True, null=True, help_text="查詢類型")
    hashed_ip = models.CharField(max_length=256, help_text="雜湊處理的IP地址")
    device_type = models.CharField(max_length=50, blank=True, null=True, help_text="設備類型")
    country = models.CharField(max_length=100, blank=True, null=True, help_text="IP來源國家")
    # 關聯請求日誌
    request_log = models.ForeignKey(RequestLog, on_delete=models.SET_NULL, null=True, blank=True, related_name="queries")
    results_count = models.IntegerField(default=0, help_text="查詢結果數量")
    processing_time = models.FloatField(null=True, blank=True, help_text="查詢處理時間(ms)")

    class Meta:
        db_table = 'query_logs'
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['search_type']),
            models.Index(fields=['hashed_ip']),
        ]
    
    @staticmethod
    def hash_ip(ip, salt="random_salt_value"):
        """用於雜湊化IP的工具方法"""
        return hashlib.sha256(f"{ip}{salt}".encode()).hexdigest()
    
    def __str__(self):
        return f"{self.query[:30]}... ({self.timestamp})"


class PopularQuery(models.Model):
    """熱門查詢統計"""
    query = models.CharField(max_length=255, unique=True, help_text="查詢內容")
    frequency = models.PositiveIntegerField(default=0, help_text="出現次數")
    last_searched = models.DateTimeField(auto_now=True, help_text="最後一次查詢的時間")
    category = models.CharField(max_length=50, blank=True, null=True, help_text="查詢類別")
    click_count = models.PositiveIntegerField(default=0, help_text="點擊次數")
    
    class Meta:
        db_table = 'popular_queries'
        indexes = [
            models.Index(fields=['frequency']),
            models.Index(fields=['last_searched']),
            models.Index(fields=['category']),
        ]
        verbose_name_plural = "Popular Queries"
    
    def increment_search(self):
        """增加查詢次數"""
        self.frequency += 1
        self.save(update_fields=['frequency', 'last_searched'])
    
    def increment_click(self):
        """增加點擊次數"""
        self.click_count += 1
        self.save(update_fields=['click_count', 'last_searched'])
    
    def __str__(self):
        return f"{self.query[:30]}... ({self.frequency}次)"


class IPLimit(models.Model):
    """IP限制管理"""
    hashed_ip = models.CharField(max_length=256, unique=True, help_text="雜湊處理的IP地址")
    last_request = models.DateTimeField(auto_now=True, help_text="最近一次查詢的時間")
    request_count = models.PositiveIntegerField(default=0, help_text="當前時間窗口內的查詢次數")
    is_blocked = models.BooleanField(default=False, help_text="是否被封鎖")
    block_reason = models.TextField(blank=True, null=True, help_text="封鎖原因")
    block_until = models.DateTimeField(null=True, blank=True, help_text="封鎖至何時")
    total_request_count = models.PositiveIntegerField(default=0, help_text="歷史總請求次數")
    
    class Meta:
        db_table = 'ip_limits'
        indexes = [
            models.Index(fields=['is_blocked']),
            models.Index(fields=['last_request']),
        ]
    
    @staticmethod
    def hash_ip(ip, salt="random_salt_value"):
        """用於雜湊化IP的工具方法"""
        return hashlib.sha256(f"{ip}{salt}".encode()).hexdigest()
    
    def __str__(self):
        status = "已封鎖" if self.is_blocked else "正常"
        return f"{self.hashed_ip[:10]}... ({status})"


class CRUDLog(models.Model):
    """資料操作日誌"""
    ACTION_TYPES = [
        ("create", "創建"),
        ("update", "更新"),
        ("delete", "刪除"),
        ("read", "讀取"),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, help_text="操作用戶")
    app_name = models.CharField(max_length=50, help_text="應用名稱")
    model_name = models.CharField(max_length=50, help_text="模型名稱")
    action_type = models.CharField(max_length=10, choices=ACTION_TYPES, help_text="操作類型")
    data_snapshot = models.JSONField(help_text="資料快照")
    timestamp = models.DateTimeField(auto_now_add=True, help_text="操作時間")
    # 新增欄位
    object_id = models.CharField(max_length=100, help_text="被操作對象的ID")
    ip_address = models.GenericIPAddressField(null=True, blank=True, help_text="操作IP")
    changes = models.JSONField(null=True, blank=True, help_text="具體變更內容")
    request_log = models.ForeignKey(RequestLog, on_delete=models.SET_NULL, null=True, blank=True, related_name="crud_logs")
    
    class Meta:
        db_table = 'crud_logs'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['app_name', 'model_name']),
            models.Index(fields=['action_type']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['object_id']),
        ]

    def __str__(self):
        username = self.user.username if self.user else "匿名"
        return f"{username} - {self.get_action_type_display()} - {self.model_name} ({self.timestamp})"


class ErrorLog(models.Model):
    """錯誤日誌"""
    ERROR_LEVELS = [
        ("debug", "Debug"),
        ("info", "Info"),
        ("warning", "Warning"),
        ("error", "Error"),
        ("critical", "Critical"),
    ]
    
    level = models.CharField(max_length=10, choices=ERROR_LEVELS, help_text="錯誤等級")
    message = models.TextField(help_text="錯誤訊息")
    timestamp = models.DateTimeField(auto_now_add=True, help_text="發生時間")
    traceback = models.TextField(null=True, blank=True, help_text="堆疊追蹤")
    request_log = models.ForeignKey(RequestLog, on_delete=models.SET_NULL, null=True, blank=True, related_name="errors")
    handled = models.BooleanField(default=False, help_text="是否已處理")
    handled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="handled_errors")
    handled_at = models.DateTimeField(null=True, blank=True, help_text="處理時間")
    
    class Meta:
        db_table = 'error_logs'
        indexes = [
            models.Index(fields=['level']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['handled']),
        ]
    
    def __str__(self):
        return f"{self.get_level_display()} - {self.message[:50]}... ({self.timestamp})"


class PerformanceMetric(models.Model):
    """性能指標"""
    METRIC_TYPES = [
        ("api_response", "API響應時間"),
        ("database_query", "資料庫查詢"),
        ("template_render", "模板渲染"),
        ("background_task", "背景任務"),
    ]
    
    metric_type = models.CharField(max_length=20, choices=METRIC_TYPES, help_text="指標類型")
    name = models.CharField(max_length=100, help_text="指標名稱")
    value = models.FloatField(help_text="指標值")
    unit = models.CharField(max_length=20, help_text="單位")
    timestamp = models.DateTimeField(auto_now_add=True, help_text="記錄時間")
    details = models.JSONField(null=True, blank=True, help_text="詳細資訊")
    request_log = models.ForeignKey(RequestLog, on_delete=models.SET_NULL, null=True, blank=True, related_name="performance_metrics")
    
    class Meta:
        db_table = 'performance_metrics'
        indexes = [
            models.Index(fields=['metric_type']),
            models.Index(fields=['name']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.value} {self.unit} ({self.timestamp})"

class ContactMessage(models.Model):
    """聯絡我們表單訊息（公開頁面送出，供管理員後台檢視）"""
    name = models.CharField("姓名", max_length=100)
    email = models.EmailField("電子郵件")
    phone = models.CharField("聯絡電話", max_length=30, blank=True, null=True)
    message = models.TextField("訊息內容")
    is_handled = models.BooleanField("是否已處理", default=False)
    created_at = models.DateTimeField("建立時間", auto_now_add=True)

    class Meta:
        db_table = 'contact_messages'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_handled']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.name} <{self.email}> ({self.created_at})"
