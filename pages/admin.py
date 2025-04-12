from django.contrib import admin
from .models import Page
from admin.models import BaseAdmin
from django.utils.html import format_html


@admin.register(Page)
class PageAdmin(BaseAdmin):
    list_display = ['title', 'app_related', 'link_redirect', 'active']
    list_editable = ['active']
    search_fields = ['title']
    list_filter=['active']

    def link_redirect(self, obj):
        return format_html(
            """<a style="display: flex; align-items: center; gap: 4px" href="{}" target="_blank">
                {}
            </a>""",
            obj.url,
            obj.url
        )

    link_redirect.short_description = "Url"




