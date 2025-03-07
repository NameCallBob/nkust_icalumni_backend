# Generated by Django 5.0.2 on 2024-12-21 15:12

import ckeditor.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AlumniAssociation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', ckeditor.fields.RichTextField(help_text='支援 HTML 標籤', verbose_name='簡介')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='建立時間')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新時間')),
            ],
        ),
        migrations.CreateModel(
            name='AlumniAssociationImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_type', models.CharField(choices=[('large', '大圖'), ('small', '小圖')], max_length=10, verbose_name='圖片類型')),
                ('file', models.ImageField(upload_to='static/info/alumni_association_images/', verbose_name='圖片檔案')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True, verbose_name='上傳時間')),
                ('is_active', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Constitution',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', ckeditor.fields.RichTextField()),
                ('pdf_file', models.FileField(upload_to='static/info/constitutions/', verbose_name='章程 PDF 檔案')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='建立時間')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新時間')),
            ],
        ),
        migrations.CreateModel(
            name='ConstitutionImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_type', models.CharField(choices=[('large', '大圖'), ('small', '小圖')], max_length=10, verbose_name='圖片類型')),
                ('file', models.ImageField(upload_to='static/info/constitution_images/', verbose_name='圖片檔案')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True, verbose_name='上傳時間')),
                ('is_active', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='MembershipRequirement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', ckeditor.fields.RichTextField(help_text='支援 HTML 標籤', verbose_name='入會條件')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='建立時間')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新時間')),
            ],
        ),
        migrations.CreateModel(
            name='MembershipRequirementImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_type', models.CharField(choices=[('large', '大圖'), ('small', '小圖')], max_length=10, verbose_name='圖片類型')),
                ('file', models.ImageField(upload_to='static/info/membership_requirement_images/', verbose_name='圖片檔案')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True, verbose_name='上傳時間')),
                ('is_active', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='OrganizationalStructure',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', ckeditor.fields.RichTextField(help_text='支援 HTML 標籤', verbose_name='職責描述')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='建立時間')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新時間')),
            ],
        ),
        migrations.CreateModel(
            name='OrganizationalStructureImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_type', models.CharField(choices=[('large', '大圖'), ('small', '小圖')], max_length=10, verbose_name='圖片類型')),
                ('file', models.ImageField(upload_to='static/info/organizational_structure_images/', verbose_name='圖片檔案')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True, verbose_name='上傳時間')),
                ('is_active', models.BooleanField()),
            ],
        ),
    ]
