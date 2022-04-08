from django.contrib import admin

from .models import Reviews, Comment, User


class ReviewsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'score', 'author', 'title')
    search_fields = ('title', 'author')
    list_filter = ('score', 'text',)
    empty_value_display = '-пусто-'


admin.site.register(Reviews, ReviewsAdmin)
admin.site.register(Comment)
admin.site.register(User)
