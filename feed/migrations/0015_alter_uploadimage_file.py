# Generated by Django 3.2.6 on 2021-09-02 18:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feed', '0014_alter_uploadimage_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadimage',
            name='file',
            field=models.ImageField(upload_to='images'),
        ),
    ]
