from django.db import models

class PromotionAd(models.Model):
    image = models.ImageField(upload_to='static/promotion_ads/')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class ContinuousAd(models.Model):
    image = models.ImageField(upload_to='static/continuous_ads/')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class OtherImage(models.Model):
    type = models.TextField(default="None", null=False)
    image = models.ImageField(upload_to='staic/other_images/')
    title = models.CharField(max_length=255,null=True)
    description = models.TextField(blank=True, null=True)   
    created_at = models.DateTimeField(auto_now_add=True)
