from django.contrib import admin
from .models import Page, SubPage
from admin.models import BaseAdmin
from django.utils.html import format_html

class SubPageAdminInline(admin.TabularInline):
    model = SubPage
    extra = 0
    list_display = ['title']


@admin.register(Page)
class PageAdmin(BaseAdmin):
    inlines = [SubPageAdminInline]
    list_display = ['title', 'subpages_list', 'link_redirect', 'active']
    list_editable = ['active']
    search_fields = ['title']
    list_filter=['active']

    def subpages_list(self, obj):
        subpages = obj.subpages.all()  
        return ", ".join([sub.title for sub in subpages])

    subpages_list.short_description = "Subpáginas"

    def link_redirect(self, obj):
        return format_html(
            """<a style="display: flex; align-items: center; gap: 4px" href="{}" target="_blank">
                {}
            </a>""",
            obj.url,
            obj.url
        )

    link_redirect.short_description = "Url"




