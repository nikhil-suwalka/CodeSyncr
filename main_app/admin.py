from django.contrib import admin

# Register your models here.

from .models import *


# class FileAdmin(admin.ModelAdmin):
#     readonly_fields = ('last_changed',)


admin.site.register(Session)
# admin.site.register(File, FileAdmin)
admin.site.register(File)
admin.site.register(Diff)
