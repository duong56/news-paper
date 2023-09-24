from django.contrib import admin

# Register your models here.
from about import models
# Register your models here.

admin.site.register(models.Partner)
admin.site.register(models.AboutContent)