# Generated by Django 5.1 on 2024-10-18 17:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ventas', '0010_delete_metodoenvio_alter_carrito_created_at_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CodigoPromocional',
        ),
        migrations.RemoveField(
            model_name='producto',
            name='especificaciones_tecnicas',
        ),
        migrations.RemoveField(
            model_name='producto',
            name='etiqueta',
        ),
        migrations.AlterField(
            model_name='carrito',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='producto',
            name='stock',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
