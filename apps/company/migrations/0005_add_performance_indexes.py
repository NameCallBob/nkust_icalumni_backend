from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0004_alter_company_member'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='company',
            index=models.Index(fields=['clicks'], name='company_clicks_idx'),
        ),
        migrations.AddIndex(
            model_name='company',
            index=models.Index(fields=['created_at'], name='company_created_at_idx'),
        ),
    ]
