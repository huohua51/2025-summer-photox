from django.db import models

class Tag(models.Model):
    id = models.PositiveIntegerField(primary_key=True, verbose_name='标签ID')
    name = models.CharField(max_length=50, unique=True, verbose_name='标签名称')

    class Meta:
        verbose_name = '标签'
        verbose_name_plural = '标签管理'
        ordering = ['id']

    def __str__(self):
        return f"{self.id}:{self.name}"