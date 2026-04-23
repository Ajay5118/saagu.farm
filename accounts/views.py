import json
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import User, Address


def login_view(request):
    if request.user.is_authenticated:
        return redirect('store:home')
    return render(request, 'accounts/login.html', {
        'firebase_config': settings.FIREBASE_CONFIG,
    })


@require_POST
def firebase_verify_view(request):
    """Receive Firebase ID token from the frontend, verify it, and log the user in."""
    try:
        data = json.loads(request.body)
        id_token = data.get('id_token', '').strip()
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid request body'}, status=400)

    if not id_token:
        return JsonResponse({'error': 'id_token is required'}, status=400)

    # Verify token with Firebase Admin SDK
    try:
        import firebase_admin
        from firebase_admin import auth as firebase_auth, credentials

        if not firebase_admin._apps:
            cred_path = settings.FIREBASE_CREDENTIALS_PATH
            if not cred_path.exists():
                return JsonResponse(
                    {'error': 'Firebase credentials not configured on server. '
                              'Add firebase-credentials.json to the project root.'},
                    status=503,
                )
            cred = credentials.Certificate(str(cred_path))
            firebase_admin.initialize_app(cred)

        decoded = firebase_auth.verify_id_token(id_token)
        phone = decoded.get('phone_number')

        if not phone:
            return JsonResponse({'error': 'Phone number not found in token'}, status=400)

    except Exception as e:
        return JsonResponse({'error': f'Token verification failed: {e}'}, status=401)

    user, created = User.objects.get_or_create(phone=phone)
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, user)

    next_url = request.session.pop('checkout_redirect', None)
    if created:
        return JsonResponse({'success': True, 'redirect': '/accounts/profile/'})
    return JsonResponse({'success': True, 'redirect': next_url or '/'})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('store:home')


@login_required
def profile_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        if name:
            request.user.name = name
        if email:
            request.user.email = email
        request.user.save()
        messages.success(request, 'Profile updated!')
        return redirect('accounts:profile')

    addresses = request.user.addresses.all()
    return render(request, 'accounts/profile.html', {'addresses': addresses})


@login_required
def add_address_view(request):
    if request.method == 'POST':
        Address.objects.create(
            user=request.user,
            label=request.POST.get('label', 'Home'),
            name=request.POST.get('name', ''),
            phone=request.POST.get('phone', request.user.phone),
            address_line1=request.POST.get('address_line1', ''),
            address_line2=request.POST.get('address_line2', ''),
            city=request.POST.get('city', ''),
            state=request.POST.get('state', 'Telangana'),
            pincode=request.POST.get('pincode', ''),
            is_default=request.POST.get('is_default') == 'on',
        )
        messages.success(request, 'Address saved!')
        next_url = request.POST.get('next', '')
        return redirect(next_url or 'accounts:profile')

    return render(request, 'accounts/add_address.html')


@login_required
def delete_address_view(request, pk):
    Address.objects.filter(pk=pk, user=request.user).delete()
    messages.success(request, 'Address removed.')
    return redirect('accounts:profile')
