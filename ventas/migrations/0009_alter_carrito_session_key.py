# Generated by Django 5.1 on 2024-10-18 16:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ventas', '0008_codigopromocional_metodoenvio'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carrito',
            name='session_key',
            field=models.CharField(max_length=40),
        ),
    ]
