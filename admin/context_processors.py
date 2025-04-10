from pages.models import Page, SubPage
from django.contrib import messages
from django.shortcuts import redirect

def pages_for_sidebar(request):
    pages = Page.objects.all()
    permissions = set(request.user.get_all_permissions())
    if request.user.is_authenticated:
        pages_allowed = set(request.user.pages_allowed.all())
    else:
        pages_allowed = set() 

    try:
        groups = request.user.groups.prefetch_related("permissions").all()

        for profile in groups:
            permissions.update(profile.permissions.values_list("codename", flat=True))
            """ pages_allowed.update(Page.objects.filter(groups=profile)) """

    except Exception as e:
        print(f"Erro ao obter permissões: {e}")

    if not request.user.is_superuser:
        filtered_pages = []
        for page in pages:
            path_parts = page.url.strip("/").split("/")
            if page in pages_allowed and len(path_parts) > 2 and (
                f"{path_parts[1]}.view_{path_parts[2]}" in permissions or f"view_{path_parts[2]}" in permissions
            ):
                filtered_pages.append(page)
        pages = filtered_pages




    return {
        "has_user_permission": True,
        "page_list": pages,
        "app_label": None,
    }
