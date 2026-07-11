from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0003_articleimage_priority'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='article',
            index=models.Index(fields=['active'], name='article_active_idx'),
        ),
        migrations.AddIndex(
            model_name='article',
            index=models.Index(fields=['active', 'created_at'], name='article_active_created_idx'),
        ),
    ]
