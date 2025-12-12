from django.contrib import admin
from .models import Category, Word, UserProgress, QuizResult# Скрываем ненужные разделы allauth



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ('name', 'slug')

@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ('english', 'russian', 'category')
    list_filter = ('category',)
    search_fields = ('english', 'russian')

admin.site.register(UserProgress)
admin.site.register(QuizResult)