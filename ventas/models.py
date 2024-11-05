from django.db import models
from django.utils import timezone

# Modelo para los productos
class Producto(models.Model):
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField()
    categoria = models.CharField(max_length=100)
    costo = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)  # Campo para controlar el stock
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)

    def __str__(self):
        return self.titulo

# Modelo para el carrito de compras
class Carrito(models.Model):
    session_key = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Carrito de la sesión: {self.session_key}'

# Modelo para los items dentro del carrito
class CarritoItem(models.Model):
    carrito = models.ForeignKey(Carrito, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.cantidad} x {self.producto.titulo}'

    # Método para calcular el costo total de los productos en este item del carrito
    @property
    def total_costo(self):
        return self.cantidad * self.producto.costo
class CodigoPromocional(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    descuento = models.DecimalField(max_digits=5, decimal_places=2)  # Porcentaje de descuento, ej. 10.00 para 10%
    es_valor_fijo = models.BooleanField(default=False)  # True si el descuento es un valor fijo en vez de porcentaje
    fecha_expiracion = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.codigo

    def es_valido(self):
        if self.fecha_expiracion:
            return self.fecha_expiracion > timezone.now()
        return True