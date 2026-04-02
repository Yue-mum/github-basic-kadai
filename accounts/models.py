#models.pyには、SQLを書かずにデータベースの作成、取得、更新、削除（CRUD）操作が可能
#ここに書くのは、ユーザーモデルとメール認証、パスワードリセットのトークンモデル


from django.contrib.auth.models import (
    #AbstractBaseUserは、パスワードのハッシュ化（不規則な文字列に変換する）や認証などの最低限のユーザーモデルの機能を提供するクラス
    AbstractBaseUser,
    #BaseUserManagerは
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils import timezone
#ユーザーを作るクラス
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('メールアドレスは必須です')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_email_verified', True)
        return self.create_user(email, password, **extra_fields)
    

class User(AbstractBaseUser, PermissionsMixin):
    #会員区別の定義
    MEMBER_TYPE_FREE = 0
    MEMBER_TYPE_PAID = 1
    MEMBER_TYPE_CHOICES = [
        (MEMBER_TYPE_FREE, '無料会員'),
        (MEMBER_TYPE_PAID, '有料会員'),
    ]
    #利用状態の定義
    STATUS_ACTIVE = 0
    STATUS_STOP = 1
    STATUS_CHOICES = [
        (STATUS_ACTIVE, '有効'),
        (STATUS_STOP, '停止')
    ]

    #フィールドの定義
    email = models.EmailField('メールアドレス', unique=True)#unique=Trueは、同じメールアドレスを持つユーザーが複数存在できないようにするための設定
    name = models.CharField('氏名', max_length=100)
    phone = models.CharField('電話番号', max_length=20, blank=True)

    member_type = models.IntegerField(
        '会員状態', 
        choices=MEMBER_TYPE_CHOICES,
        default=MEMBER_TYPE_FREE,
    )

    status = models.IntegerField(
        '利用状態',
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE,
        )
    is_email_verified = models.BooleanField('メール認証済み', default=True)

    #管理者画面に必要な情報
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    date_joined = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)#レコードが最初に作成されたときの日時を自動的に保存するフィールド
    updated_at = models.DateTimeField(auto_now=True)#レコードが更新されたときの日時を自動的に保存するフィールド
    #AbstractBaseUser
    USERNAME_FIELD = 'email'#ログイン時のにメールアドレスでログインする
    REQUIRED_FIELDS = ['name']
    #モデル操作をUserManager()でする設定
    objects = UserManager()

    class Meta: 
        verbose_name = '会員'
        verbose_name_plural = '会員一覧'

    def __str__(self):
        return self.name
    
    #有料会員判定
    @property#@propertyは、クラスのメソッドを属性のようにアクセスできるようにするためのデコレーター
    def is_paid(self):
        return self.member_type == self.MEMBER_TYPE_PAID
    #停止ユーザー判定
    @property
    def is_suspended(self):
        return self.status == self.STATUS_STOP
    
    #メール認証
class EmailVerificationToken(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,#ユーザーが削除されたときに、関連するトークンも削除されるようにするための設定
        related_name='verification_token',#UserモデルからEmailVerificationTokenモデルにアクセスするときの名前の指定
    )
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name ='メール認証トークン'
    def __str__(self):
        return f'{self.user.email}のトークン'
    
#パスワード再設定
class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=64,unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'PW再設定トークン'
    def __str__(self):
        return f'{self.user.email}のリセットトークン'