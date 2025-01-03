from django.urls import path
from books import views
from .views import BooksListView, make_payment, verify_payment, BookDetailView, CartView, AddToCartView, RemoveFromCartView, BookCheckoutView, paymentComplete, SearchResultsListView, CheckoutView, PlaceOrderView, PaymentSuccessView, PaymentFailureView

urlpatterns = [
    path('', BooksListView.as_view(), name='list'),
    path('<int:pk>/', BookDetailView.as_view(), name='detail'),
    path('<int:pk>/add-to-cart/', AddToCartView.as_view(), name='add_to_cart'),
    path('<int:pk>/checkout/', BookCheckoutView.as_view(), name='checkout'),
    path('complete/', paymentComplete, name='complete'),
    path('search/', SearchResultsListView.as_view(), name='search_results'),
    path('cart/', CartView.as_view(), name='cart'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('makepayment/', make_payment, name='make_payment'),
    path('payment-success/', PaymentSuccessView.as_view(), name='payment_success'),
    path('payment-failure/', PaymentFailureView.as_view(), name='payment_failure'),
    path('verify_payment/', verify_payment, name='verify_payment'),  
    path('place-order/', PlaceOrderView.as_view(), name='place_order'),
    path('remove-from-cart/<int:book_id>/', RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('sendmail/', views.sendmail, name='sendmail'),
]
