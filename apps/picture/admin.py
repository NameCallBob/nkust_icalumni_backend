from django.contrib import admin
from apps.picture.models import SelfImage,SlideImage,CompanyImage,ProductImage

admin.site.register(SelfImage)
admin.site.register(SlideImage)
admin.site.register(CompanyImage)
admin.site.register(ProductImage)