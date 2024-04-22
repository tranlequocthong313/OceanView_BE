from django.apps import apps

from app.admin import admin_site

apartment_app = apps.get_app_config("feedback")

for model_name, model in apartment_app.models.items():
    admin_site.register(model)
