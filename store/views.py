from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Avg, Sum, Count
from django.utils import timezone
from datetime import timedelta
from django.contrib.admin.views.decorators import staff_member_required


from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema


from .forms import DhakaThreadsSignupForm
from .models import User, Product, Category, Review, Order, OrderItem


@swagger_auto_schema(method='get', operation_description="Boutique Home: List products with filters")
@api_view(['GET'])
def home(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    
    size_filter = request.GET.get('size')
    color_filter = request.GET.get('color')
    category_id = request.GET.get('category')

    if size_filter:
        products = products.filter(size=size_filter)
    if color_filter:
        products = products.filter(color__iexact=color_filter)
    if category_id:
        products = products.filter(category_id=category_id)

    sort_by = request.GET.get('sort')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'popular':
        products = products.order_by('-stock')

    return render(request, 'store/home.html', {
        'products': products,
        'categories': categories,
    })

@swagger_auto_schema(method='get', operation_description="View product details and reviews")
@api_view(['GET', 'POST'])
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    reviews = product.reviews.all().order_by('-created_at')
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    if request.method == 'POST' and request.user.is_authenticated:
        Review.objects.create(
            product=product,
            user=request.user,
            rating=request.POST.get('rating'),
            comment=request.POST.get('comment')
        )
        return redirect('product_detail', pk=product.pk)
            
    return render(request, 'store/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'average_rating': average_rating,
    })


@swagger_auto_schema(method='post', operation_description="User Registration with Email Activation")
@api_view(['GET', 'POST'])
def signup(request):
    if request.method == 'POST':
        form = DhakaThreadsSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            link = f"{request.scheme}://{request.get_host()}/activate/{uid}/{token}/"
            
            send_mail(
                'Activate your Dhaka Threads Account',
                f'Welcome! Please click the link to activate your account: {link}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email]
            )
            return render(request, 'store/activation_sent.html')
    else:
        form = DhakaThreadsSignupForm()
    return render(request, 'store/signup.html', {'form': form})

@api_view(['GET'])
def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('home')
    return render(request, 'store/activation_invalid.html')



@api_view(['GET'])
def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    p_id = str(product_id)
    cart[p_id] = cart.get(p_id, 0) + 1
    request.session['cart'] = cart
    return redirect('cart_detail')

@api_view(['GET'])
def cart_detail(request):
    cart = request.session.get('cart', {})
    products_list = []
    total = 0
    for p_id, quantity in cart.items():
        product = get_object_or_404(Product, id=p_id)
        subtotal = product.price * quantity
        total += subtotal
        products_list.append({'product': product, 'quantity': quantity, 'subtotal': subtotal})
        
    return render(request, 'store/cart.html', {'cart_items': products_list, 'total': total})

@api_view(['GET'])
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    p_id = str(product_id)
    if p_id in cart:
        del cart[p_id]
        request.session['cart'] = cart
    return redirect('cart_detail')



@swagger_auto_schema(method='post', operation_description="Process checkout and send confirmation email")
@api_view(['GET', 'POST'])
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart: return redirect('home')
    
    total = sum(get_object_or_404(Product, id=p_id).price * qty for p_id, qty in cart.items())

    if request.method == 'POST':
        order = Order.objects.create(
            user=request.user,
            full_name=request.POST.get('full_name'),
            address=request.POST.get('address'),
            total_amount=total,
            status='Pending'
        )
        for p_id, qty in cart.items():
            product = get_object_or_404(Product, id=p_id)
            OrderItem.objects.create(order=order, product=product, quantity=qty, price=product.price)
        
       
        try:
            send_mail(
                f'Order #{order.id} Confirmed',
                f'Hi {order.full_name}, your order of ৳{total} is successful!',
                settings.EMAIL_HOST_USER,
                [request.user.email]
            )
        except Exception as e: print(f"Email error: {e}")

        request.session['cart'] = {}
        return render(request, 'store/order_success.html', {'order': order})

    return render(request, 'store/checkout.html', {'total': total})

@api_view(['GET'])
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/order_history.html', {'orders': orders})



@api_view(['GET'])
def toggle_wishlist(request, product_id):
    wishlist = request.session.get('wishlist', [])
    if product_id in wishlist: wishlist.remove(product_id)
    else: wishlist.append(product_id)
    request.session['wishlist'] = wishlist
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@api_view(['GET'])
def wishlist_detail(request):
    wishlist_ids = request.session.get('wishlist', [])
    products = Product.objects.filter(id__in=wishlist_ids)
    return render(request, 'store/wishlist.html', {'products': products})

@staff_member_required
@api_view(['GET'])
def admin_dashboard(request):
    now = timezone.now()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0)
    start_of_last_month = (start_of_month - timedelta(days=1)).replace(day=1)
    
    context = {
        'current_month_sales': Order.objects.filter(created_at__gte=start_of_month).aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
        'last_month_sales': Order.objects.filter(created_at__gte=start_of_last_month, created_at__lt=start_of_month).aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
        'purchases_last_week': Order.objects.filter(created_at__gte=now - timedelta(days=7)).count(),
        'purchases_last_month': Order.objects.filter(created_at__gte=start_of_month).count(),
        'top_users': User.objects.annotate(order_count=Count('order')).order_by('-order_count')[:5],
        'popular_products': Product.objects.annotate(num_orders=Count('orderitem')).order_by('-num_orders')[:5],
    }
    return render(request, 'store/admin_dashboard.html', context)


from rest_framework import generics
from .serializers import ProductSerializer


class ProductListAPI(generics.ListAPIView):
    """
    API endpoint that allows products to be viewed as a list.
    Proof of DRF: Uses generics.ListAPIView for automatic GET handling.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductDetailAPI(generics.RetrieveAPIView):
    """
    API endpoint that returns a single product by ID.
    Proof of DRF: Uses generics.RetrieveAPIView.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer