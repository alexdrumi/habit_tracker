from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users' #this has to be renamed because users are not 'top level' app, its inside 'apps'
