from django.contrib import admin
from .models import Article, Category
from markdownx.admin import MarkdownxModelAdmin
# Register your models here.

admin.site.register(Category, MarkdownxModelAdmin)
admin.site.register(Article, MarkdownxModelAdmin)
