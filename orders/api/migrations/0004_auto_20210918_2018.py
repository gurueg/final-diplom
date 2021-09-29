# Generated by Django 2.2.13 on 2021-09-18 20:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20210918_2005'),
    ]

    operations = [
        migrations.AlterField(
            model_name='modelparameter',
            name='product_model',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parameters', to='api.ProductModel', verbose_name='Модель'),
        ),
    ]
