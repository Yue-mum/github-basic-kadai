from django.db import models


class ServiceSettings(models.Model):
    service_name = models.CharField('サービス名', max_length=100, default='名古屋グルメ')
    logo = models.ImageField('ロゴ', upload_to='service/', blank=True, null=True)
    contact_email = models.EmailField('お問い合わせメールアドレス', blank=True)
    terms = models.TextField('利用規約', blank=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        verbose_name = 'サービス設定'
        
    def __str__(self):
        return self.service_name