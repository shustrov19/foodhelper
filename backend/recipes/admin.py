from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                     ShoppingList, Tag, TagRecipe)


class IngredientsInline(admin.TabularInline):
    """
    Функционал для добавления ингридиентов в рецепты сразу из пункта Рецепты.
    """
    model = IngredientRecipe


class TagsInline(admin.TabularInline):
    """
    Функционал для добавления тегов в рецепты сразу из пункта Рецепты.
    """
    model = TagRecipe


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    list_filter = ('author', 'name', 'tags')
    inlines = (IngredientsInline, TagsInline)


class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(Favorite)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientRecipe)
admin.site.register(Tag, TagAdmin)
admin.site.register(TagRecipe)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(ShoppingList)
