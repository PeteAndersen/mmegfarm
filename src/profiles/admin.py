from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from .models import Profile, Account, CreatureInstance, GlyphInstance, Team


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False


class AccountInline(admin.StackedInline):
    model = Account
    can_delete = True


admin.site.unregister(User)


@admin.register(User)
class UserWithProfileAdmin(UserAdmin):
    inlines = [
        ProfileInline,
        AccountInline,
    ]


@admin.register(CreatureInstance)
class CreatureInstanceAdmin(admin.ModelAdmin):
    pass


@admin.register(GlyphInstance)
class GlyphInstanceAdmin(admin.ModelAdmin):
    pass


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    pass
