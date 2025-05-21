from django.shortcuts import render

def index(request):
    # Renderiza la landing page: templates/orders/index.html
    return render(request, 'orders/index.html')

def menu(request):
    # Renderiza la página del menú: templates/orders/menu.html
    return render(request, 'orders/menu.html')

def pago(request):
    # Renderiza el formulario de pago: templates/orders/pago.html
    return render(request, 'orders/pago.html')