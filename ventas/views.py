
from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto, Carrito, CarritoItem , CodigoPromocional
from django.utils import timezone
from django.shortcuts import redirect
from decimal import Decimal
from .forms import CheckoutForm
import mercadopago
from django.db import transaction
from django.conf import settings
from django.urls import reverse
from django.http import JsonResponse
import json
sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)




# Vista para agregar un producto al carrito

def agregar_al_carrito(request, producto_id):
    # Verifica si el carrito ya tiene un ID en la sesión
    carrito_id = request.session.get('carrito', None)
    
    if carrito_id is None:
        # Si no existe un carrito en la sesión, crea uno nuevo
        nuevo_carrito = Carrito.objects.create()  # Ajusta esto según tu modelo Carrito
        carrito_id = nuevo_carrito.id
        request.session['carrito'] = carrito_id
    
    # Inicia una transacción atómica para la operación de base de datos
    with transaction.atomic():
        # Obtener el producto o devolver un 404 si no existe
        producto = get_object_or_404(Producto, id=producto_id)
        
        # Intenta obtener o crear el CarritoItem correspondiente
        item, created = CarritoItem.objects.get_or_create(carrito_id=carrito_id, producto=producto)
        
        if not created:
            # Si el item ya existía, incrementa la cantidad
            item.cantidad += 1
        item.save()

    return redirect('ver_carrito')

# Vista para ver el contenido del carrito
def calcular_total_carrito(carrito):
    total = 0
    for item in carrito:
        total += item.producto.costo * item.cantidad
    return total

def ver_carrito(request):
    # Obtener el ID del carrito de la sesión
    carrito_id = request.session.get('carrito', None)
    items = CarritoItem.objects.filter(carrito_id=carrito_id) if carrito_id else []
    
    # Calcular subtotal y total de cada ítem
    item_totals = []
    subtotal = Decimal(0)
    for item in items:
        item_total = Decimal(item.producto.costo) * item.cantidad
        item_totals.append({'item': item, 'item_total': item_total})
        subtotal += item_total

    envio = Decimal(100)  # Costo de envío fijo (por ejemplo)

    # Obtener el descuento desde la sesión y aplicar si es válido
    descuento_valor = request.session.get('descuento', {})
    descuento = Decimal(0)
    
    if isinstance(descuento_valor, dict) and 'tipo' in descuento_valor and 'monto' in descuento_valor:
        # Asegúrate de manejar el valor adecuadamente según su tipo
        if descuento_valor['tipo'] == 'fijo':
            descuento = Decimal(descuento_valor['monto'])
        elif descuento_valor['tipo'] == 'porcentaje':
            descuento = subtotal * (Decimal(descuento_valor['monto']) / Decimal(100))

    # Calcular el total aplicando el descuento
    total = subtotal + envio - descuento

    context = {
        'items': item_totals,
        'subtotal': subtotal,
        'envio': envio,
        'descuento': descuento,
        'total': total,
        'codigo_aplicado': request.session.get('codigo_aplicado', None),
    }

    return render(request, 'carrito.html', context)


# Vista para eliminar un producto del carrito
def eliminar_del_carrito(request, item_id):
    item = get_object_or_404(CarritoItem, id=item_id)
    item.delete()
    return redirect('ver_carrito')

# Vista para actualizar la cantidad de un producto en el carrito


def actualizar_carrito(request, producto_id):
    carrito_id = request.session.get('carrito', None)
    if carrito_id is None:
        return redirect('ver_carrito')  # Redirige si no hay carrito en la sesión

    if request.method == 'POST':
        nueva_cantidad = int(request.POST.get('cantidad', 1))
        
        # Obtén el item en el carrito
        item = CarritoItem.objects.filter(carrito_id=carrito_id, producto_id=producto_id).first()
        
        if item:
            if nueva_cantidad > 0:
                item.cantidad = nueva_cantidad
                item.save()
            else:
                item.delete()  # Elimina el item si la cantidad es 0

    return redirect('ver_carrito')
# Vista para vaciar el carrito
def vaciar_carrito(request):
    session_key = request.session.session_key
    if not session_key:
        return redirect('ver_carrito')
    
    carrito = Carrito.objects.filter(session_key=session_key).first()
    if carrito:
        carrito.items.all().delete()
    
    return redirect('ver_carrito')
def productos_view(request):
    productos = Producto.objects.all()  # Obtiene todos los productos de la base de datos
    return render(request, 'productos.html', {'productos': productos})

# views.py


def aplicar_codigo_promocional(request):
    if request.method == 'POST':
        codigo = request.POST.get('codigo_promocional', '').strip()

        try:
            codigo_obj = CodigoPromocional.objects.get(codigo=codigo)

            if codigo_obj.es_valido():
                descuento = {
                    'tipo': 'fijo' if codigo_obj.es_valor_fijo else 'porcentaje',
                    'monto': float(codigo_obj.descuento)
                }
                request.session['descuento'] = descuento
                request.session['codigo_aplicado'] = codigo
            else:
                # Si el código ha expirado
                request.session['descuento'] = None
                request.session['codigo_aplicado'] = None

        except CodigoPromocional.DoesNotExist:
            # Si el código no existe
            request.session['descuento'] = None
            request.session['codigo_aplicado'] = None

    return redirect('ver_carrito')
def eliminar_codigo_promocional(request):
    if 'descuento' in request.session:
        del request.session['descuento']
    return redirect('ver_carrito')



def checkout_view(request):
    # Inicializar Mercado Pago con el Access Token
    sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)

    # Obtener el ID del carrito de la sesión
    carrito_id = request.session.get('carrito', None)
    items = CarritoItem.objects.filter(carrito_id=carrito_id) if carrito_id else []

    # Calcular el subtotal y el total de cada ítem
    item_totals = []
    subtotal = Decimal(0)
    for item in items:
        item_total = Decimal(item.producto.costo) * item.cantidad
        item_totals.append({'item': item, 'item_total': item_total})
        subtotal += item_total

    envio = Decimal(100)

    # Obtener el descuento desde la sesión
    descuento_valor = request.session.get('descuento', {})
    descuento = Decimal(0)
    if isinstance(descuento_valor, dict) and 'tipo' in descuento_valor and 'monto' in descuento_valor:
        if descuento_valor['tipo'] == 'fijo':
            descuento = Decimal(descuento_valor['monto'])
        elif descuento_valor['tipo'] == 'porcentaje':
            descuento = subtotal * (Decimal(descuento_valor['monto']) / Decimal(100))

    # Calcular el total
    total = subtotal + envio - descuento

    # Crear la preferencia de pago para Mercado Pago
    preference_data = {
        "items": [
            {
                "title": "Compra en Carteras Farias",
                "quantity": 1,
                "unit_price": float(total)  # Mercado Pago requiere float para el precio
            }
        ],
        "back_urls": {
            "success": request.build_absolute_uri(reverse("pago_exitoso")),
            "failure": request.build_absolute_uri(reverse("pago_fallido")),
            "pending": request.build_absolute_uri(reverse("pago_pendiente")),
        },
        "auto_return": "approved",
    }
    preference_response = sdk.preference().create(preference_data)
    preference_id = preference_response["response"]["id"]

    # Crear el formulario de checkout
    form = CheckoutForm()

    context = {
        'form': form,
        'items': item_totals,
        'subtotal': subtotal,
        'envio': envio,
        'descuento': descuento,
        'total': total,
        'preference_id': preference_id,
        'public_key': settings.MERCADO_PAGO_PUBLIC_KEY,
    }

    return render(request, 'checkout.html', context)
    # views.py


def pago_exitoso(request):
    return render(request, "pago_exitoso.html")

def pago_fallido(request):
    return render(request, "pago_fallido.html")

def pago_pendiente(request):
    return render(request, "pago_pendiente.html")

    
def procesar_pago(request):
    if request.method == "POST":
        sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
        
        # Extrae los datos del frontend
        data = json.loads(request.body)

        payment_data = {
            "transaction_amount": data.get("transaction_amount"),  # Cambia a transaction_amount
            "token": data.get("token"),
            "description": "Compra en Carteras Farias",
            "installments": int(data.get("installments", 1)),
            "payment_method_id": data.get("payment_method_id"),  # Cambia a payment_method_id
            "payer": {
                "email": data.get("payer", {}).get("email"),  # Asegúrate de que el email del pagador esté incluido
                "identification": {
                    "type": data.get("payer", {}).get("identification", {}).get("type"),
                    "number": data.get("payer", {}).get("identification", {}).get("number"),
                }
            }
        }

        # Realizar el pago en Mercado Pago
        payment_response = sdk.payment().create(payment_data)
        payment = payment_response["response"]

        # Log completo de la respuesta para ver todos los detalles
        print("Respuesta de Mercado Pago:", payment)

        # Revisa y retorna el resultado
        if payment.get("status") == "approved":
            return JsonResponse({"status": "approved"})
        else:
            error_message = payment.get("status_detail", "Error desconocido en el pago")
            return JsonResponse({"status": "failure", "message": error_message})

    return JsonResponse({"status": "failure", "message": "Método no permitido"}, status=405)