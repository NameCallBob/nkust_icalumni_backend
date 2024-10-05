from django.db import models
from apps.company.models import Company
from ckeditor.fields import RichTextField

class Recruit(models.Model):
    company = models.ForeignKey(Company,on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    intro = RichTextField
    click = models.IntegerField(default=0)
    deadline = models.DateField()
    release_date = models.DateField(auto_now_add=True)