# Generated by Django 5.0.1 on 2024-10-14 18:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posting_blogs', '0004_rename_follower_followers_followed_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='followers',
            name='status',
            field=models.CharField(blank=True, choices=[('accepted', 'ACCEPTED'), ('rejected', 'REJECTED'), ('pending', 'PENDING')], max_length=20, null=True),
        ),
    ]