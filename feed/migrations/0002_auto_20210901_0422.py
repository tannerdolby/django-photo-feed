# Generated by Django 3.2.6 on 2021-09-01 04:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feed', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Car',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('price', models.DecimalField(decimal_places=2, max_digits=5)),
                ('photo', models.ImageField(upload_to='cars')),
            ],
        ),
        migrations.AddField(
            model_name='image',
            name='image',
            field=models.ImageField(default='null.png', upload_to='images'),
            preserve_default=False,
        ),
    ]
