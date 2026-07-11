from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('member', '0005_add_outstanding_alumni_sort_order_and_school'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='member',
            index=models.Index(fields=['is_paid'], name='member_is_paid_idx'),
        ),
        migrations.AddIndex(
            model_name='member',
            index=models.Index(fields=['is_show'], name='member_is_show_idx'),
        ),
        migrations.AddIndex(
            model_name='member',
            index=models.Index(fields=['gender'], name='member_gender_idx'),
        ),
        migrations.AddIndex(
            model_name='member',
            index=models.Index(fields=['name'], name='member_name_idx'),
        ),
    ]
