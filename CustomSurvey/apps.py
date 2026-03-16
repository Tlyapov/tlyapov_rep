from django.apps import AppConfig


class CustomsurveyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'CustomSurvey'
    verbose_name = "Кастомные опросы"
