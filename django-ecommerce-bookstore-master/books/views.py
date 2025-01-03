from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin 
from .models import Book, Order, Cart
from django.urls import reverse_lazy
from django.db.models import Q # for search method
from django.http import JsonResponse
import json
from django.views import View
from django.contrib.auth.decorators import login_required
import razorpay
from django.conf import settings

class BooksListView(ListView):
    model = Book
    template_name = 'list.html'
    context_object_name = 'books'

class BookDetailView(DetailView):
    model = Book
    template_name = 'detail.html'

    def post(self, request, *args, **kwargs):
        book_id = self.kwargs['pk']
        book = Book.objects.get(id=book_id)
        cart = request.session.get('cart', {})
        quantity = request.POST.get('quantity', 1)
        if book_id in cart:
            cart[book_id] += int(quantity)
        else:
            cart[book_id] = int(quantity)

        request.session['cart'] = cart
        return redirect('cart')

class SearchResultsListView(ListView):
    model = Book
    template_name = 'search_results.html'

    def get_queryset(self): 
        query = self.request.GET.get('q')
        return Book.objects.filter(
            Q(title__icontains=query) | Q(author__icontains=query) | Q(category__icontains=query)
        )

class CartView(View):
    template_name = 'cart.html'

    def get(self, request):
        cart = request.session.get('cart', {})
        books = Book.objects.filter(id__in=cart.keys())

        customer = request.user if request.user.is_authenticated else None  

        cart_items = [
            {
                "book": book,
                "quantity": cart[str(book.id)],
                "total_price": book.price * cart[str(book.id)],
            }
            for book in books
        ]
        total_cost = sum(item["total_price"] for item in cart_items)

        return render(request, self.template_name, {
            'cart_items': cart_items,
            'total_cost': total_cost,
            'customer': customer,  
        })

    def post(self, request):
        cart = request.session.get('cart', {})
        book_id = request.POST.get('book_id')
        quantity = int(request.POST.get('quantity', 1))  

        if book_id in cart:
            cart[book_id] += quantity  
        else:
            cart[book_id] = quantity  

        request.session['cart'] = cart
        return redirect('cart')

class AddToCartView(View):
    def get(self, request, pk):
        book = Book.objects.get(pk=pk)
        cart = request.session.get('cart', {})

        if str(book.pk) in cart:
            cart[str(book.pk)] += 1
        else:
            cart[str(book.pk)] = 1

        request.session['cart'] = cart

        return redirect('detail', pk=pk)

class RemoveFromCartView(View):
    def post(self, request, book_id):
        cart = request.session.get('cart', {})

        if str(book_id) in cart:
            del cart[str(book_id)]

        request.session['cart'] = cart

        return redirect('cart')

    def get(self, request, book_id):
        return self.post(request, book_id)  

class CheckoutView(View):
    template_name = 'checkout.html'

    def get(self, request):
        cart = request.session.get('cart', {})
        books = Book.objects.filter(id__in=cart.keys())

        cart_items = [
            {
                "book": book,
                "quantity": cart[str(book.id)],
                "total_price": book.price * cart[str(book.id)],
                "available": book.book_available, 
            }
            for book in books
        ]

        total_cost = sum(item["total_price"] for item in cart_items if item["available"])

        return render(request, self.template_name, {
            'cart_items': cart_items,
            'total_cost': total_cost,
        })

@login_required
def checkout(request):
    try:
        cart = request.user.cart  
        cart_items = cart.cart_items.all()
        total_cost = cart.total_amount
    except Cart.DoesNotExist:
        cart_items = []
        total_cost = 0

    return render(request, 'checkout.html', {'cart_items': cart_items, 'total_cost': total_cost})

class PlaceOrderView(View):
    def post(self, request):
        cart = request.session.get('cart', {})
        user = request.user

        for book_id, quantity in cart.items():
            book = Book.objects.get(id=book_id)
            Order.objects.create(user=user, book=book, quantity=quantity)

        request.session['cart'] = {}

        return redirect('complete') 

class BookCheckoutView(LoginRequiredMixin, DetailView):
    model = Book
    template_name = 'checkout.html'
    login_url = 'login'

def paymentComplete(request):
    body = json.loads(request.body)
    print('BODY:', body)
    product = Book.objects.get(id=body['productId'])
    Order.objects.create(product=product)
    return JsonResponse('Payment completed!', safe=False)

from django.shortcuts import render, redirect
from .models import PaymentDetail

def pay_view(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        contact = request.POST['contact']
        address = request.POST['address']
        city = request.POST['city']
        state = request.POST['state']
        pincode = request.POST['pincode']
        amount = request.POST['amount']

        payment_detail = PaymentDetail.objects.create(
            name=name,
            email=email,
            contact=contact,
            address=address,
            city=city,
            state=state,
            pincode=pincode,
            amount=amount,
        )

        return redirect('razorpay_payment_url')

    return render(request, 'pay.html', {'amount': 500.00})

@login_required
def make_payment(request):
    try:
        cart = request.session.get('cart', {})
        books = Book.objects.filter(id__in=cart.keys())
        total_cost = sum(book.price * cart[str(book.id)] for book in books)

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        order_amount = int(total_cost * 100)
        order_currency = "INR"
        order_receipt = f"order_rcptid_{request.user.id}"
        notes = {"purpose": "Estore Checkout"}

        order = client.order.create({
            "amount": order_amount,
            "currency": order_currency,
            "receipt": order_receipt,
            "notes": notes
        })

        context = {
            "data": order,
            "amount": total_cost,
            "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        }
        return render(request, "pay.html", context)

    except Exception as e:
        return render(request, "cart.html", {"error": str(e)})

def sendmail(request):
    return render(request, "list.html")

class PaymentSuccessView(View):
    def get(self, request):
        return render(request, 'success.html')

class PaymentFailureView(View):
    def get(self, request):
        return render(request, 'failure.html')
    
def verify_payment(request):
    if request.method == "POST":
        data = request.POST
        razorpay_order_id = data['razorpay_order_id']
        razorpay_payment_id = data['razorpay_payment_id']
        razorpay_signature = data['razorpay_signature']

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        params_dict = {
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature,
        }

        try:
            client.utility.verify_payment_signature(params_dict)
            return render(request, "success.html")
        except razorpay.errors.SignatureVerificationError:
            return render(request, "failure.html")
