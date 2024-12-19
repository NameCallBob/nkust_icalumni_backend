from rest_framework.viewsets import ModelViewSet
from apps.record.models import ContactForm
from apps.record.serializer import ContactFormSerializer
from IC_alumni.permission.staff import IsStaffOrCreateOnly

class ContactFormViewSet(ModelViewSet):
    queryset = ContactForm.objects.all().order_by('-created_at')
    serializer_class = ContactFormSerializer
    permission_classes = [IsStaffOrCreateOnly]
