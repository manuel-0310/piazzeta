from rest_framework import serializers
from .models import Order, OrderItem, Dish

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['dish', 'quantity', 'unit_price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    user  = serializers.StringRelatedField(read_only=True)  # muestra username

    class Meta:
        model = Order
        fields = ['id', 'user', 'customer_name', 'phone', 'address',
                  'status', 'created_at', 'items']


    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        for item in items_data:
            OrderItem.objects.create(order=order, **item)
        return order


class DishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dish
        # Incluye aquí todos los campos que desees exponer
        fields = ['id', 'name', 'category', 'description', 'price', 'image_url']

