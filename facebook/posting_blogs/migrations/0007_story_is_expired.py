# Generated by Django 5.0.1 on 2024-10-25 10:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posting_blogs', '0006_story'),
    ]

    operations = [
        migrations.AddField(
            model_name='story',
            name='is_expired',
            field=models.BooleanField(default=False),
        ),
    ]
