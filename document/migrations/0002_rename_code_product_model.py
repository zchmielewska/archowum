# Generated by Django 3.2.9 on 2021-12-03 17:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='code',
            new_name='model',
        ),
    ]
