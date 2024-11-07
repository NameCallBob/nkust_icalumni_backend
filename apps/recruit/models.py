from django.db import models
from apps.company.models import Company
from ckeditor.fields import RichTextField

# 圖片上傳路徑
def upload_to_images(instance, filename):
    return f'static/recruit/{filename}'

# Recruit 模型
class Recruit(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    intro = RichTextField()
    info_clicks = models.IntegerField(default=0)
    deadline = models.DateField()
    release_date = models.DateField(auto_now_add=True)
    active = models.BooleanField("是否發布",default=True)

class Contact(models.Model):
    recruit = models.OneToOneField(Recruit, related_name='contact', on_delete=models.CASCADE)
    company_name = models.TextField(default="公司名稱?")
    name = models.TextField()
    phone = models.TextField()
    email = models.EmailField()

# 圖片資料庫
class RecruitImage(models.Model):
    IMAGE_TYPE_CHOICES = [
        ('large', 'Large Image'),
        ('small', 'Small Image'),
    ]

    recruit = models.ForeignKey(Recruit, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='static/recruit/')
    image_type = models.CharField(max_length=5, choices=IMAGE_TYPE_CHOICES)  # 透過此欄位區分圖片類型

    def __str__(self):
        return f"{self.get_image_type_display()} for {self.recruit.title}"
