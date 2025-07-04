# Generated by Django 4.1.7 on 2025-06-26 07:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('albums', '0003_initial'),
        ('community', '0002_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='like',
            options={'verbose_name': '点赞', 'verbose_name_plural': '点赞'},
        ),
        migrations.AlterUniqueTogether(
            name='like',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='comment',
            name='is_deleted',
            field=models.BooleanField(default=False, verbose_name='是否删除'),
        ),
        migrations.AddField(
            model_name='comment',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='community.comment', verbose_name='父评论'),
        ),
        migrations.AddField(
            model_name='comment',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='更新时间'),
        ),
        migrations.AddField(
            model_name='like',
            name='like_type',
            field=models.CharField(choices=[('album', '相册'), ('comment', '评论'), ('image', '图片')], default=0, max_length=20, verbose_name='点赞类型'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='like',
            name='object_id',
            field=models.PositiveIntegerField(default=0, verbose_name='对象ID'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='album',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='albums.album', verbose_name='相册'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='创建时间'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='用户'),
        ),
        migrations.AlterField(
            model_name='like',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='创建时间'),
        ),
        migrations.AlterField(
            model_name='like',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='用户'),
        ),
        migrations.AlterUniqueTogether(
            name='like',
            unique_together={('user', 'like_type', 'object_id')},
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notification_type', models.CharField(choices=[('like', '点赞'), ('comment', '评论'), ('follow', '关注'), ('system', '系统通知')], max_length=20, verbose_name='通知类型')),
                ('content', models.TextField(verbose_name='通知内容')),
                ('is_read', models.BooleanField(default=False, verbose_name='是否已读')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('sender', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sent_notifications', to=settings.AUTH_USER_MODEL, verbose_name='发送用户')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL, verbose_name='接收用户')),
            ],
            options={
                'verbose_name': '通知',
                'verbose_name_plural': '通知',
                'ordering': ['-created_at'],
            },
        ),
        migrations.RemoveField(
            model_name='like',
            name='album',
        ),
        migrations.CreateModel(
            name='Follow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='关注时间')),
                ('follower', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='following', to=settings.AUTH_USER_MODEL, verbose_name='关注者')),
                ('following', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='followers', to=settings.AUTH_USER_MODEL, verbose_name='被关注者')),
            ],
            options={
                'verbose_name': '关注关系',
                'verbose_name_plural': '关注关系',
                'unique_together': {('follower', 'following')},
            },
        ),
    ]
