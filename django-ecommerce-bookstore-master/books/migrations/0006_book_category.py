# Generated by Django 5.1.4 on 2025-01-02 11:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0005_paymentdetail'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='category',
            field=models.CharField(choices=[('Fiction', 'Fiction'), ('Non-Fiction', 'Non-Fiction'), ('Children', 'Children'), ('Text Books', 'Text Books')], default='Fiction', max_length=20),
        ),
    ]
