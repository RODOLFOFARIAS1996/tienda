from django import forms

class CheckoutForm(forms.Form):
    nombre = forms.CharField(max_length=100)
    direccion = forms.CharField(max_length=255)
    email = forms.EmailField()
    # Otros campos según lo necesario
