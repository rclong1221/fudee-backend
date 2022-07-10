from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from fudee.users.forms import UserAdminChangeForm, UserAdminCreationForm
from fudee.users.models import User_Image

User = get_user_model()

@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    readonly_fields = ("uuid",)
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("name", "first_name", "middle_name", "last_name", "email", "uuid")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    list_display = ["username", "name", "is_superuser"]
    search_fields = ["name"]

admin.site.register(User_Image)
