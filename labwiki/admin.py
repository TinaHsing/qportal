from django.contrib import admin
from .models import Article
from markdownx.admin import MarkdownxModelAdmin
# Register your models here.

admin.site.register(Article, MarkdownxModelAdmin)
