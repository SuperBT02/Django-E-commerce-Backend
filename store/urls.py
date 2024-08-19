from django.urls import path
from . import views
from rest_framework_nested import routers

router = routers.DefaultRouter()
router.register('products', views.ProductViewSet, basename='product')
router.register('collections', views.CollectionViewSet)
router.register('cart', views.CartViewSet)
router.register('customers', views.CustomerViewSet)
router.register('orders', views.OrderViewSet, basename='orders')
# nested routers
products_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
products_router.register('reviews', views.ReviewViewSet, basename='product-reviews')

cart_router = routers.NestedDefaultRouter(router,'cart', lookup='cart')
cart_router.register('items', views.CartItemViewSet, basename='cart-items-details')
# URLConf
urlpatterns = router.urls + products_router.urls + cart_router.urls
# path('product/<pk>/', views.ProductDetails.as_view()),
# path('collections/', views.Collection_List.as_view(), name='collection-list'),
