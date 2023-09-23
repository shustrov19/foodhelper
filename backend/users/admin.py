from django.contrib import admin

from .models import Follow, User

admin.site.site_title = 'Админ-панель сайта Foodgram'
admin.site.site_header = 'Админ-панель сайта Foodgram'


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name')
    list_filter = ('email', 'username')


class FollowAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'following')


admin.site.register(User, UserAdmin)
admin.site.register(Follow, FollowAdmin)
