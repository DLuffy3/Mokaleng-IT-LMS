from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from learning_management_app.models import UserType


# Register your models here.

class UserModel(UserAdmin):
    pass


admin.site.register(UserType, UserModel)
