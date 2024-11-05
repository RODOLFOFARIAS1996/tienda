from .models import Carrito

def carrito_total_items(request):
    total_items = 0
    if request.user.is_authenticated:  # Si los usuarios necesitan estar logueados para comprar
        carrito = Carrito.objects.filter(session_key=request.session.session_key).first()
        if carrito:
            total_items = sum(item.cantidad for item in carrito.items.all())
    return {'total_items': total_items}
