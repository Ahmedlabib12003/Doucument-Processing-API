# Generated by Django 5.1.4 on 2025-01-09 11:35

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('file_path', models.CharField(max_length=500)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('width', models.IntegerField(null=True)),
                ('height', models.IntegerField(null=True)),
                ('channels', models.IntegerField(null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PDF',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('file_path', models.CharField(max_length=500)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('num_pages', models.IntegerField(null=True)),
                ('page_width', models.FloatField(null=True)),
                ('page_height', models.FloatField(null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
