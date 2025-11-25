from django.shortcuts import redirect

def system_settings(request):
    return redirect("/admin/settings/settings/1/change/")