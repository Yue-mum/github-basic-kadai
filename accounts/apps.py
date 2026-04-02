from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'#モデルの主キーに使用するフィールドのデフォルトタイプを指定する。BigAutoFieldは大きな整数を自動的に生成するフィールドタイプで、デフォルトで使用されるように設定されている。
    name = 'accounts'
