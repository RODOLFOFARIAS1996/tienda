from django.urls import path
from . import views

urlpatterns = [
    path('productos/', views.productos_view, name='productos'),
    path('agregar_al_carrito/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('eliminar_del_carrito/<int:item_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('actualizar_carrito/<int:producto_id>/', views.actualizar_carrito, name='actualizar_carrito'),
    path('aplicar-codigo/', views.aplicar_codigo_promocional, name='aplicar_codigo_promocional'),
    path('eliminar-codigo/', views.eliminar_codigo_promocional, name='eliminar_codigo_promocional'),
    path('checkout/', views.checkout_view, name='checkout'),  # Cambiado para no duplicar
    path('procesar_pago/', views.procesar_pago, name='procesar_pago'),
    path('pago-exitoso/', views.pago_exitoso, name='pago_exitoso'),
    path('pago-fallido/', views.pago_fallido, name='pago_fallido'),
    path('pago-pendiente/', views.pago_pendiente, name='pago_pendiente'),
]
