# Generated by Django 2.1.2 on 2018-10-20 18:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0002_team'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='user',
            new_name='owner',
        ),
    ]
