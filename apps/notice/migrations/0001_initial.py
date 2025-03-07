# Generated by Django 5.0.2 on 2024-12-21 15:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('member', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_notifications', models.BooleanField(default=True)),
                ('sms_notifications', models.BooleanField(default=False)),
                ('news_notifications', models.BooleanField(default=True)),
                ('promo_notifications', models.BooleanField(default=True)),
                ('member', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='notification_setting', to='member.member')),
            ],
        ),
    ]
