# Generated by Django 3.2.7 on 2021-09-30 01:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jazzboardapi', '0007_delete_comcomment'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='anonymous',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='comment',
            name='hidden',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='text',
            name='anonymous',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='text',
            name='hidden',
            field=models.BooleanField(default=False),
        ),
    ]
