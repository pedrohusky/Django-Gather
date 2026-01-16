from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .forms import SignUpForm, SignInForm
from .models import Realm, Profile
import json


def home(request):
    """Landing page"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html')


def signup(request):
    """User registration"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('dashboard')
    else:
        form = SignUpForm()
    
    return render(request, 'auth/signup.html', {'form': form})


def signin(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = SignInForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
    else:
        form = SignInForm()
    
    return render(request, 'auth/signin.html', {'form': form})


def signout(request):
    """User logout"""
    logout(request)
    return redirect('home')


@login_required
def dashboard(request):
    """Dashboard with realm list"""
    realms = Realm.objects.filter(owner=request.user)
    return render(request, 'app/dashboard.html', {'realms': realms})


@login_required
def play(request, realm_id):
    """Game page"""
    realm = get_object_or_404(Realm, id=realm_id)
    return render(request, 'play/play.html', {
        'realm': realm,
        'realm_id': realm_id,
        'user_id': request.user.id,
        'username': request.user.username,
        'skin': request.user.profile.skin
    })


@login_required
@require_http_methods(["POST"])
def create_realm(request):
    """Create a new realm"""
    try:
        data = json.loads(request.body)
        name = data.get('name', 'My Realm')
        map_data = data.get('map_data', {})
        
        realm = Realm.objects.create(
            owner=request.user,
            name=name,
            map_data=map_data
        )
        
        return JsonResponse({
            'success': True,
            'realm_id': realm.id,
            'share_id': str(realm.share_id)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
def get_realm(request, realm_id):
    """Get realm data"""
    realm = get_object_or_404(Realm, id=realm_id)
    return JsonResponse({
        'id': realm.id,
        'name': realm.name,
        'share_id': str(realm.share_id),
        'map_data': realm.map_data,
        'only_owner': realm.only_owner,
        'owner_id': realm.owner.id
    })


@login_required
@require_http_methods(["POST"])
def update_profile(request):
    """Update user profile"""
    try:
        data = json.loads(request.body)
        profile = request.user.profile
        
        if 'skin' in data:
            profile.skin = data['skin']
        
        if 'visited_realms' in data:
            profile.visited_realms = data['visited_realms']
        
        profile.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
