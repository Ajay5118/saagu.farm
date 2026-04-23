def cart_count(request):
    """Make cart count available in all templates."""
    cart = request.session.get('cart', {})
    return {'cart_count': sum(cart.values())}
