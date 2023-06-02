from django.contrib import admin

from .models import SyncConfig, SyncedRecord, UserConnection

admin.site.register(UserConnection)
admin.site.register(SyncConfig)
admin.site.register(SyncedRecord)
