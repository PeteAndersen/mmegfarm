# Generated by Django 2.0.6 on 2018-06-28 19:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bestiary', '0003_auto_20180628_0157'),
    ]

    operations = [
        migrations.AddField(
            model_name='spell',
            name='slot',
            field=models.IntegerField(default=1),
        ),
    ]
