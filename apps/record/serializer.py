from rest_framework import serializers
from apps.record.models import ContactForm

class ContactFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactForm
        fields = '__all__'


