# Generated by Django 4.0 on 2022-03-22 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_emailverificationstatus'),
    ]

    operations = [
        migrations.AddField(
            model_name='videodata',
            name='video_thumbnail',
            field=models.ImageField(blank=True, null=True, upload_to='thumbnailPhotos'),
        ),
    ]
