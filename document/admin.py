from django.contrib import admin

from document import models


admin.site.register(models.Product)
admin.site.register(models.Category)
admin.site.register(models.Document)
