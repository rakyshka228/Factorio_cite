from django.contrib import admin

from .models import Blueprint, Comment, Like, Tag


@admin.register(Blueprint)
class BlueprintAdmin(admin.ModelAdmin):
	list_display = ('title', 'author', 'created_at', 'like_count')
	list_filter = ('created_at', 'tags')
	search_fields = ('title', 'description', 'author__username')
	prepopulated_fields = {'slug': ('title',)}


admin.site.register(Tag)
admin.site.register(Like)
admin.site.register(Comment)
