from django.contrib import admin

from .models import Follow, User

admin.site.site_title = 'Админ-панель сайта FoodHelper'
admin.site.site_header = 'Админ-панель сайта FoodHelper'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Отображение пользователей."""
    list_display = ('id', 'username', 'email', 'first_name', 'last_name')
    list_filter = ('email', 'username')


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Отображение подписок."""
    list_display = ('id', 'user', 'following')
