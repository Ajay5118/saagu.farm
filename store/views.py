import json
import hmac
import hashlib
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.conf import settings
from .models import Product, ProductVariant, Order, OrderItem
from accounts.models import Address


def home_view(request):
    """Main landing page with products."""
    products = Product.objects.filter(is_available=True).prefetch_related('variants')
    context = {
        'products': products,
        'products_json': json.dumps({
            str(v.id): {
                'product_id': p.id,
                'product_name': p.name,
                'variant_id': v.id,
                'weight': v.weight,
                'weight_grams': v.weight_grams,
                'price': float(v.price),
                'mrp': float(v.mrp),
                'badge': p.badge,
                'category': p.category,
            }
            for p in products
            for v in p.variants.filter(is_available=True)
        }),
    }
    return render(request, 'store/home.html', context)


# ── Session-based Cart ──────────────────────────────────────────────────────

def _get_cart(request):
    """Get cart from session. Format: {variant_id: quantity}"""
    return request.session.get('cart', {})


def _save_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True


@require_POST
def add_to_cart(request):
    """Add a product variant to session cart."""
    variant_id = str(request.POST.get('variant_id', ''))
    qty = int(request.POST.get('quantity', 1))

    # Validate variant exists
    try:
        variant = ProductVariant.objects.get(id=variant_id, is_available=True)
    except ProductVariant.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=400)

    cart = _get_cart(request)
    cart[variant_id] = cart.get(variant_id, 0) + qty
    _save_cart(request, cart)

    total_items = sum(cart.values())
    return JsonResponse({
        'success': True,
        'cart_count': total_items,
        'message': f'{variant.product.name} ({variant.weight}) added to cart!'
    })


@require_POST
def update_cart(request):
    """Update quantity of a cart item."""
    variant_id = str(request.POST.get('variant_id', ''))
    qty = int(request.POST.get('quantity', 0))

    cart = _get_cart(request)
    if qty <= 0:
        cart.pop(variant_id, None)
    else:
        cart[variant_id] = qty
    _save_cart(request, cart)

    return JsonResponse({'success': True, 'cart_count': sum(cart.values())})


@require_POST
def remove_from_cart(request):
    """Remove an item from cart."""
    variant_id = str(request.POST.get('variant_id', ''))
    cart = _get_cart(request)
    cart.pop(variant_id, None)
    _save_cart(request, cart)
    return JsonResponse({'success': True, 'cart_count': sum(cart.values())})


def cart_view(request):
    """Show cart page."""
    cart = _get_cart(request)
    items = []
    subtotal = 0

    for variant_id, qty in cart.items():
        try:
            variant = ProductVariant.objects.select_related('product').get(id=variant_id)
            line_total = variant.price * qty
            subtotal += line_total
            items.append({
                'variant': variant,
                'quantity': qty,
                'line_total': line_total,
            })
        except ProductVariant.DoesNotExist:
            continue

    delivery_charge = 0 if subtotal >= 500 else 50
    total = subtotal + delivery_charge

    return render(request, 'store/cart.html', {
        'items': items,
        'subtotal': subtotal,
        'delivery_charge': delivery_charge,
        'total': total,
    })


# ── Checkout ────────────────────────────────────────────────────────────────

@login_required
def checkout_view(request):
    """Checkout — select address and confirm order."""
    cart = _get_cart(request)
    if not cart:
        messages.warning(request, 'Your cart is empty!')
        return redirect('store:home')

    # Build cart items
    items = []
    subtotal = 0
    for variant_id, qty in cart.items():
        try:
            variant = ProductVariant.objects.select_related('product').get(id=variant_id)
            line_total = variant.price * qty
            subtotal += line_total
            items.append({'variant': variant, 'quantity': qty, 'line_total': line_total})
        except ProductVariant.DoesNotExist:
            continue

    delivery_charge = 0 if subtotal >= 500 else 50
    total = subtotal + delivery_charge
    addresses = request.user.addresses.all()

    return render(request, 'store/checkout.html', {
        'items': items,
        'subtotal': subtotal,
        'delivery_charge': delivery_charge,
        'total': total,
        'addresses': addresses,
    })


def _build_order(request, address, notes, payment_method,
                  razorpay_order_id='', razorpay_payment_id=''):
    """Create an Order from the current session cart. Returns the Order or None."""
    cart = _get_cart(request)
    if not cart:
        return None

    order = Order.objects.create(
        user=request.user,
        address=address,
        delivery_name=address.name,
        delivery_phone=address.phone,
        delivery_address=(
            f"{address.address_line1}, {address.address_line2}, "
            f"{address.city}, {address.state}"
        ),
        delivery_pincode=address.pincode,
        notes=notes,
        payment_method=payment_method,
        razorpay_order_id=razorpay_order_id,
        razorpay_payment_id=razorpay_payment_id,
    )

    subtotal = 0
    for variant_id, qty in cart.items():
        try:
            variant = ProductVariant.objects.select_related('product').get(id=variant_id)
            OrderItem.objects.create(
                order=order,
                product=variant.product,
                variant=variant,
                product_name=variant.product.name,
                weight=variant.weight,
                price=variant.price,
                quantity=qty,
            )
            subtotal += variant.price * qty
        except ProductVariant.DoesNotExist:
            continue

    delivery_charge = 0 if subtotal >= 500 else 50
    order.subtotal = subtotal
    order.delivery_charge = delivery_charge
    order.total = subtotal + delivery_charge
    order.status = 'confirmed'
    order.save()

    _save_cart(request, {})
    return order


@login_required
@require_POST
def place_order(request):
    """COD checkout — create order directly."""
    cart = _get_cart(request)
    if not cart:
        return JsonResponse({'error': 'Cart is empty'}, status=400)

    address_id = request.POST.get('address_id')
    address = get_object_or_404(Address, id=address_id, user=request.user)

    order = _build_order(
        request, address,
        notes=request.POST.get('notes', ''),
        payment_method='cod',
    )
    messages.success(request, f'Order #{order.order_id} placed! Pay on delivery.')
    return redirect('store:order_confirmation', order_id=order.order_id)


@login_required
@require_POST
def razorpay_create_order(request):
    """Create a Razorpay order and return the details needed by the frontend."""
    try:
        import razorpay
    except ImportError:
        return JsonResponse({'error': 'razorpay package not installed'}, status=503)

    cart = _get_cart(request)
    if not cart:
        return JsonResponse({'error': 'Cart is empty'}, status=400)

    subtotal = sum(
        ProductVariant.objects.get(id=vid).price * qty
        for vid, qty in cart.items()
    )
    delivery_charge = 0 if subtotal >= 500 else 50
    amount_paise = int((subtotal + delivery_charge) * 100)

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    rz_order = client.order.create({
        'amount':          amount_paise,
        'currency':        'INR',
        'payment_capture': 1,
    })

    return JsonResponse({
        'razorpay_order_id': rz_order['id'],
        'amount':            amount_paise,
        'currency':          'INR',
        'key_id':            settings.RAZORPAY_KEY_ID,
    })


@login_required
@require_POST
def razorpay_verify_payment(request):
    """Verify Razorpay payment signature and create the Django order."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid request'}, status=400)

    rz_order_id  = data.get('razorpay_order_id', '')
    payment_id   = data.get('razorpay_payment_id', '')
    signature    = data.get('razorpay_signature', '')
    address_id   = data.get('address_id')
    notes        = data.get('notes', '')

    # Verify HMAC-SHA256 signature
    expected = hmac.new(
        key=settings.RAZORPAY_KEY_SECRET.encode(),
        msg=f"{rz_order_id}|{payment_id}".encode(),
        digestmod=hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(expected, signature):
        return JsonResponse({'error': 'Payment verification failed'}, status=400)

    address = get_object_or_404(Address, id=address_id, user=request.user)
    order = _build_order(
        request, address,
        notes=notes,
        payment_method='razorpay',
        razorpay_order_id=rz_order_id,
        razorpay_payment_id=payment_id,
    )

    return JsonResponse({
        'success':  True,
        'redirect': f"/order/{order.order_id}/",
    })


@login_required
def order_confirmation_view(request, order_id):
    """Show order confirmation."""
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    return render(request, 'store/order_confirmation.html', {'order': order})


@login_required
def my_orders_view(request):
    """List user's past orders."""
    orders = Order.objects.filter(user=request.user).prefetch_related('items')
    return render(request, 'store/my_orders.html', {'orders': orders})
