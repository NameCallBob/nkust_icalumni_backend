from django.db import models

class ContactForm(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True, null=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"
    
import hashlib

class QueryLogs(models.Model):
    query = models.TextField()  # 使用者查詢內容
    timestamp = models.DateTimeField(auto_now_add=True)  # 查詢的時間
    search_type = models.CharField(max_length=50, blank=True, null=True)  # 查詢類型
    hashed_ip = models.CharField(max_length=256)  # 雜湊處理的 IP 地址
    device_type = models.CharField(max_length=50, blank=True, null=True)  # 設備類型
    country = models.CharField(max_length=100, blank=True, null=True)  # IP 來源的國家（可選）

    @staticmethod
    def hash_ip(ip, salt="random_salt_value"):
        """用於哈希化 IP 的工具方法"""
        return hashlib.sha256(f"{ip}{salt}".encode()).hexdigest()
    
class PopularQueries(models.Model):
    query = models.TextField(unique=True)  # 查詢內容
    frequency = models.PositiveIntegerField(default=0)  # 出現次數
    last_searched = models.DateTimeField(auto_now=True)  # 最後一次查詢的時間
    category = models.CharField(max_length=50, blank=True, null=True)  # 查詢類別

class IPLimits(models.Model):
    hashed_ip = models.CharField(max_length=256, unique=True)  # 雜湊處理的 IP 地址
    last_request = models.DateTimeField(auto_now=True)  # 最近一次查詢的時間
    request_count = models.PositiveIntegerField(default=0)  # 當前時間窗口內的查詢次數
    is_blocked = models.BooleanField(default=False)  # 是否被封鎖

class ClickCount(models.Model):
    query = models.TextField()  # 對應的查詢內容
    click_count = models.PositiveIntegerField(default=0)  # 點擊次數

    def increment(self):
        """增加點擊次數"""
        self.click_count += 1
        self.save()
