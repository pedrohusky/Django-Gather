from django.contrib import admin
from .models import Profile, Realm


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'skin')
    search_fields = ('user__username',)


@admin.register(Realm)
class RealmAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'created_at', 'only_owner')
    list_filter = ('only_owner', 'created_at')
    search_fields = ('name', 'owner__username')
    readonly_fields = ('share_id', 'created_at')
