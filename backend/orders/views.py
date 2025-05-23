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

from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.views import LogoutView

class CustomLogoutView(LogoutView):
    next_page = 'home'

    def dispatch(self, request, *args, **kwargs):
        """
        Cualquier petición (GET o POST) ejecuta logout
        y redirige a next_page.
        """
        # llamamos a post() para procesar el logout
        response = super().post(request, *args, **kwargs)
        return response

@login_required
def delete_order(request, pk):
    pedido = get_object_or_404(Order, pk=pk)
    pedido.delete()
    return redirect('admin_dashboard')


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

# Vista usuario: consultar sus pedidos
@login_required
def mis_pedidos(request):
    pedidos = request.user.orders.all().order_by('-created_at')
    return render(request, 'orders/mis_pedidos.html', {'pedidos': pedidos})

# Vista admin: dashboard de pedidos (ahora accesible a cualquier usuario autenticado)
from django.db.models import Q

@login_required
def admin_dashboard(request):
    # parámetros de filtro (ya tenías)
    status_filter = request.GET.get('status', '')
    client_filter = request.GET.get('client', '').strip()

    # parámetros de orden
    sort_field = request.GET.get('sort', '')         # e.g. 'customer_name' o 'status'
    direction  = request.GET.get('dir', 'asc')       # 'asc' o 'desc'

    # Base queryset
    pedidos = Order.objects.all()

    # Aplica filtros
    if status_filter in dict(Order.STATUS_CHOICES):
        pedidos = pedidos.filter(status=status_filter)
    if client_filter:
        pedidos = pedidos.filter(customer_name__icontains=client_filter)

    # Aplica orden, validando campos permitidos
    allowed_sorts = {'customer_name', 'status'}
    if sort_field in allowed_sorts:
        prefix = '' if direction == 'asc' else '-'
        pedidos = pedidos.order_by(f"{prefix}{sort_field}", '-created_at')
    else:
        # Orden por defecto
        pedidos = pedidos.order_by('-created_at')

    context = {
        'pedidos': pedidos,
        'status_filter': status_filter,
        'client_filter': client_filter,
        'sort_field':   sort_field,
        'direction':    direction,
    }
    return render(request, 'orders/admin_dashboard.html', context)

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