# Generated by Django 3.2.15 on 2023-09-02 08:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0041_order_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.CharField(choices=[('Необработанный', 'Необработанный'), ('Приготовление', 'Приготовление'), ('Доставка', 'Доставка'), ('Завершено', 'Завершено')], db_index=True, default='Необработанный', max_length=14),
        ),
    ]
