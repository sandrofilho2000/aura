from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from .views import SearchItemsView, GetJWTTokenView, CreateBillingView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

handler404 = 'django.views.defaults.page_not_found'
handler403 = 'django.views.defaults.permission_denied'

urlpatterns = [
    path('', RedirectView.as_view(url='/admin/', permanent=True)),
    path('admin/', admin.site.urls),
    path("api/search", SearchItemsView.as_view(), name="search-items"),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("api/admin-token/", GetJWTTokenView.as_view(), name="admin_token"),
    path("api/create-billing", CreateBillingView.as_view(), name="create-billing"),
]

""" path("api/update-subaccount/", UpdateSubaccountView.as_view(), name="update-subaccount"),
path("api/create-subaccount", CreateSubaccountView.as_view(), name="create-subaccount"),
path('api/delete-subaccount/<int:subaccount_id>/', DeleteSubaccountView.as_view(), name='delete-subaccount'), """

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
