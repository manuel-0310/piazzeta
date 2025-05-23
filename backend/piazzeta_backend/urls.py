from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from django.contrib.auth.decorators import login_required
from orders.views import CustomLogoutView
from orders.views import (
    index,
    menu,
    pago,
    register,
    CustomLoginView,
    CustomLogoutView,
    mis_pedidos,
    admin_dashboard,
    update_order_status,
    DishViewSet,
    OrderViewSet,
    delete_order,
)

router = routers.DefaultRouter()
router.register(r'dishes', DishViewSet, basename='dish')
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Frontend views
    path('',           index,                 name='home'),
    path('menu/',      menu,                  name='menu'),
    path('pago/',      pago,                  name='pago'),
    path('mis-pedidos/', mis_pedidos,         name='mis_pedidos'),
    path('admin-dashboard/', login_required(admin_dashboard), name='admin_dashboard'),
    path('admin-dashboard/update/<int:pk>/', update_order_status, name='update_order_status'),
    path('admin-dashboard/delete/<int:pk>/', delete_order,        name='delete_order'),

    # Authentication
    path('register/',  register,               name='register'),
    path('login/',     CustomLoginView.as_view(),  name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),

    # API REST
    path('api/', include(router.urls)),
]