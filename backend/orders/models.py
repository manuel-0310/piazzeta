from django.db import models

class Dish(models.Model):
    name        = models.CharField("Nombre", max_length=100)
    category    = models.CharField("Categoría", max_length=50, blank=True)
    description = models.TextField("Descripción", blank=True)
    price       = models.DecimalField("Precio", max_digits=8, decimal_places=2)
    image_url   = models.URLField("URL Imagen", blank=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    from django.conf import settings

    STATUS_CHOICES = [
        ('P', 'Pendiente'),
        ('E', 'Entregado'),
    ]

    customer_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=200)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
    created_at = models.DateTimeField(auto_now_add=True)
    user    = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"Pedido #{self.id} – {self.customer_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}× {self.dish.name}"
