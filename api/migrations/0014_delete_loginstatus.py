# Generated by Django 4.0 on 2022-04-03 13:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_loginstatus'),
    ]

    operations = [
        migrations.DeleteModel(
            name='LoginStatus',
        ),
    ]