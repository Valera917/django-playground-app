from django.contrib import admin
from django.contrib.admin import ModelAdmin

from store.models import Book, UserBookRelation


@admin.register(Book)
class BookAdmin(ModelAdmin):
    ...


@admin.register(UserBookRelation)
class UserBookRelationAdmin(ModelAdmin):
    ...
