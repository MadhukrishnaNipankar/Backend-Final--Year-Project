# Generated by Django 4.0 on 2022-04-11 12:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0019_remove_messages_roompass_chatroom_roompass'),
    ]

    operations = [
        migrations.AddField(
            model_name='videodata',
            name='username',
            field=models.CharField(default='', max_length=1000),
        ),
    ]