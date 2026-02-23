from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from django.http import JsonResponse
from django.utils import timezone

from campus_store.accounts.views import (
    AdminTerminalView,
    AddressViewSet,
    LoginView,
    LogoutView,
    ProfileView,
    RefreshTokenView,
    RegisterView,
    UserDirectoryViewSet,
    ResetPasswordView,
)
from campus_store.analytics.views import (
    AnalyticsOverviewView,
    CommerceInsightsView,
    MetricViewSet,
    UserStatsView,
    UserLogsView,
)
from campus_store.catalog.views import CategoryViewSet, InventoryLogViewSet, ProductViewSet
from campus_store.commerce.views import OrderViewSet
from campus_store.community.views import PostViewSet
from campus_store.focus.views import FocusVideoViewSet
from campus_store.customization.views import WishRequestViewSet
from campus_store.storefront.views import (
    StorefrontCategoryViewSet,
    StorefrontProductViewSet,
    StorefrontStoreViewSet,
)
from campus_store.wallet.views import (
    WalletConfigView,
    WalletOverviewView,
    WalletPayView,
    WalletRechargeView,
    WalletRefundView,
    WalletVoucherGenerateView,
    WalletVoucherListView,
    WalletVoucherRedeemView,
)

router = routers.DefaultRouter()
router.register(r"accounts/users", UserDirectoryViewSet, basename="user-directory")
router.register(r"accounts/addresses", AddressViewSet, basename="account-address")
router.register(r"catalog/categories", CategoryViewSet, basename="catalog-category")
router.register(r"catalog/products", ProductViewSet, basename="catalog-product")
router.register(r"catalog/inventory", InventoryLogViewSet, basename="catalog-inventory")
router.register(r"commerce/orders", OrderViewSet, basename="commerce-order")
router.register(r"customization/wishes", WishRequestViewSet, basename="customization-wish")
router.register(r"analytics/metrics", MetricViewSet, basename="analytics-metric")
router.register(r"community/posts", PostViewSet, basename="community-post")
router.register(r"focus/videos", FocusVideoViewSet, basename="focus-video")
router.register(r"storefront/stores", StorefrontStoreViewSet, basename="storefront-store")
router.register(r"storefront/products", StorefrontProductViewSet, basename="storefront-product")
router.register(r"storefront/categories", StorefrontCategoryViewSet, basename="storefront-category")

def health_view(request):
    return JsonResponse(
        {
            "status": "ok",
            "version": "1.0.0",
            "timestamp": timezone.now().isoformat(),
        }
    )

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/health/", health_view, name="health"),
    path("api/accounts/register/", RegisterView.as_view(), name="register"),
    path("api/accounts/login/", LoginView.as_view(), name="login"),
    path("api/accounts/profile/", ProfileView.as_view(), name="profile"),
    path("api/accounts/refresh/", RefreshTokenView.as_view(), name="refresh"),
    path("api/accounts/logout/", LogoutView.as_view(), name="logout"),
    path("api/accounts/reset_password/", ResetPasswordView.as_view(), name="reset-password"),
    path("api/analytics/overview/", AnalyticsOverviewView.as_view(), name="analytics-overview"),
    path("api/analytics/commerce-insights/", CommerceInsightsView.as_view(), name="analytics-commerce-insights"),
    path("api/analytics/user-stats/", UserStatsView.as_view(), name="analytics-user-stats"),
    path("api/analytics/user-logs/<int:user_id>/", UserLogsView.as_view(), name="analytics-user-logs"),
    path("api/admin/terminal/", AdminTerminalView.as_view(), name="admin-terminal"),
    path("api/wallet/", WalletOverviewView.as_view(), name="wallet-overview"),
    path("api/wallet/pay/", WalletPayView.as_view(), name="wallet-pay"),
    path("api/wallet/refund/", WalletRefundView.as_view(), name="wallet-refund"),
    path("api/wallet/config/", WalletConfigView.as_view(), name="wallet-config"),
    path("api/wallet/recharge/", WalletRechargeView.as_view(), name="wallet-recharge"),
    path("api/wallet/vouchers/generate/", WalletVoucherGenerateView.as_view(), name="wallet-voucher-generate"),
    path("api/wallet/vouchers/", WalletVoucherListView.as_view(), name="wallet-voucher-list"),
    path("api/wallet/vouchers/redeem/", WalletVoucherRedeemView.as_view(), name="wallet-voucher-redeem"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
