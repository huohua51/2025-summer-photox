# Generated by Django 5.2.3 on 2025-06-24 01:36

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.PositiveIntegerField(primary_key=True, serialize=False, verbose_name='标签ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='标签名称')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '标签',
                'verbose_name_plural': '标签管理',
                'ordering': ['id'],
            },
        ),
    ]
