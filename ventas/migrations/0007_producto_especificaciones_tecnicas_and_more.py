# Generated by Django 5.1 on 2024-10-15 17:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ventas', '0006_producto_etiqueta'),
    ]

    operations = [
        migrations.AddField(
            model_name='producto',
            name='especificaciones_tecnicas',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='producto',
            name='stock',
            field=models.IntegerField(default=0),
        ),
    ]
