from django.shortcuts import redirect

def system_integrations(request):
    return redirect("/admin/integrations/integration/1/change/")