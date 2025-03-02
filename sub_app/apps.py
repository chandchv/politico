from django.apps import AppConfig

class SubAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sub_app'
    label = 'sub_app'
    verbose_name = 'Subscription App'
    
    def ready(self):
        import sub_app.models  # Import the models 