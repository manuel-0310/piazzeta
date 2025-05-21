from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.views import LoginView, LogoutView
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Dish, Order
from .serializers import DishSerializer, OrderSerializer
from .forms import RegisterForm

# Landing, menú y pago

def index(request):
    return render(request, 'orders/index.html')

def menu(request):
    return render(request, 'orders/menu.html')

def pago(request):
    return render(request, 'orders/pago.html')

# Registro de usuario
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('menu')
    else:
        form = RegisterForm()
    return render(request, 'orders/register.html', {'form': form})

# Login y logout usando vistas genéricas
class CustomLoginView(LoginView):
    template_name = 'orders/login.html'

    def get_success_url(self):
        # Redirige a admin-dashboard si el usuario es staff
        from django.urls import reverse  # importa aquí para evitar circulares
        if self.request.user.is_staff:
            return reverse('admin_dashboard')
        # Usuarios normales van a mis-pedidos
        return reverse('mis_pedidos')

class CustomLogoutView(LogoutView):
    next_page = 'home'

# Vista usuario: consultar sus pedidos
@login_required
def mis_pedidos(request):
    pedidos = request.user.orders.all().order_by('-created_at')
    return render(request, 'orders/mis_pedidos.html', {'pedidos': pedidos})

# Vista admin: dashboard de pedidos (ahora accesible a cualquier usuario autenticado)
@login_required
def admin_dashboard(request):
    pedidos = Order.objects.all().order_by('-created_at')
    return render(request, 'orders/admin_dashboard.html', {'pedidos': pedidos})

# Actualizar estado de pedido (admin)
@login_required
def update_order_status(request, pk):
    pedido = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        nuevo_estado = request.POST.get('status')
        if nuevo_estado in dict(Order.STATUS_CHOICES):
            pedido.status = nuevo_estado
            pedido.save()
    return redirect('admin_dashboard')

# API RESTful para platos

class DishViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Dish.objects.all().order_by('id')
    serializer_class = DishSerializer

# API RESTful para pedidos
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user    
        if user.is_staff:
            return Order.objects.all().order_by('-created_at')
        return Order.objects.filter(user=user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)