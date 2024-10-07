from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto, Carrito, CarritoItem

# Vista para mostrar la lista de productos
def productos_view(request):
    productos = Producto.objects.all()
    return render(request, 'productos.html', {'productos': productos})

# Vista para agregar un producto al carrito
def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)

    # Obtener o crear el carrito de la sesión
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    carrito, created = Carrito.objects.get_or_create(session_key=session_key)
    item, created = CarritoItem.objects.get_or_create(carrito=carrito, producto=producto)
    
    # Aumentar la cantidad si el producto ya estaba en el carrito
    item.cantidad += 1
    item.save()

    return redirect('ver_carrito')

# Vista para ver el contenido del carrito
def ver_carrito(request):
    session_key = request.session.session_key
    if not session_key:
        return render(request, 'carrito.html', {'items': []})

    carrito = Carrito.objects.filter(session_key=session_key).first()
    items = carrito.items.all() if carrito else []
    return render(request, 'carrito.html', {'items': items})

# Vista para eliminar un producto del carrito
def eliminar_del_carrito(request, item_id):
    item = get_object_or_404(CarritoItem, id=item_id)
    item.delete()
    return redirect('ver_carrito')