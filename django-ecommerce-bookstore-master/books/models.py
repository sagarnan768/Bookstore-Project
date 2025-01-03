from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Book(models.Model):
    CATEGORY_CHOICES = [
        ('Fiction', 'Fiction'),
        ('Non-Fiction', 'Non-Fiction'),
        ('Children', 'Children'),
        ('Text Books', 'Text Books')
    ]

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    description = models.CharField(max_length=500, default=None)
    price = models.FloatField(null=True, blank=True)
    image_url = models.CharField(max_length=2083, default=False)
    follow_author = models.CharField(max_length=2083, blank=True)
    book_available = models.BooleanField(default=False)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='Fiction')

    def __str__(self):
        return self.title

class Order(models.Model):
    product = models.ForeignKey(Book, max_length=200, null=True, blank=True, on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product.title

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart")

    def __str__(self):
        return f"{self.user.username}'s Cart"

    @property
    def total_amount(self):
        """Calculate the total cost of all items in the cart."""
        return sum(item.total_price for item in self.cart_items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_items")
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_price(self):
        """Calculate the total price of this item (price * quantity)."""
        return self.quantity * self.book.price

    def __str__(self):
        return f"{self.book.title} - {self.quantity}"

class PaymentDetail(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    contact = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    pincode = models.CharField(max_length=10)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(
        max_length=20, 
        choices=[('Pending', 'Pending'), ('Completed', 'Completed')], 
        default='Pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - ₹{self.amount}"
