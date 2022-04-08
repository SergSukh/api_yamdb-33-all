# Generated by Django 2.2.16 on 2022-04-07 18:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0003_auto_20220408_0129'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='reviews',
            constraint=models.UniqueConstraint(fields=('author', 'title'), name='unique_followers'),
        ),
    ]
