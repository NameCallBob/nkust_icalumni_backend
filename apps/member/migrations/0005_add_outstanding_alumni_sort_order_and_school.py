# Generated manually
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('member', '0004_alter_graduate_grade_alter_graduate_school_and_more'),
    ]

    operations = [
        # Add sort_order to OutstandingAlumni
        migrations.AddField(
            model_name='outstandingalumni',
            name='sort_order',
            field=models.IntegerField(default=0, help_text='數字越小排序越前', verbose_name='排序順序'),
        ),

        # Add Meta options to OutstandingAlumni
        migrations.AlterModelOptions(
            name='outstandingalumni',
            options={'ordering': ['sort_order', '-date_awarded'], 'verbose_name': '傑出系友', 'verbose_name_plural': '傑出系友'},
        ),

        # Create SchoolOutstandingAlumni model
        migrations.CreateModel(
            name='SchoolOutstandingAlumni',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('achievements', models.TextField(blank=True, null=True, verbose_name='傑出成就')),
                ('is_featured', models.BooleanField(default=False, verbose_name='是否展示於官網')),
                ('highlight', models.CharField(max_length=100, verbose_name='傑出事蹟摘要')),
                ('date_awarded', models.DateField(blank=True, null=True, verbose_name='授予日期')),
                ('sort_order', models.IntegerField(default=0, help_text='數字越小排序越前', verbose_name='排序順序')),
                ('member', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='school_outstanding_alumni', to='member.member')),
            ],
            options={
                'ordering': ['sort_order', '-date_awarded'],
                'verbose_name': '傑出校友',
                'verbose_name_plural': '傑出校友',
            },
        ),
    ]