from pages.models import Page, SubPage

def pages_for_sidebar(request):
    user = request.user
    all_pages = Page.objects.filter(active=True).prefetch_related("subpages")
    allowed_pages = []

    if user.is_superuser:
        allowed_pages = all_pages
    else:
        user_permissions = user.get_all_permissions()
        for page in all_pages:
            app_label = page.app_related
            has_permission = any(perm.startswith(f"{app_label}.") for perm in user_permissions)

            if has_permission:
                allowed_pages.append(page)

    return {
        "has_user_permission": True,
        "page_list": allowed_pages,
        "app_label": None,
    }
