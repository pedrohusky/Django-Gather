from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .forms import SignUpForm, SignInForm
from .models import Realm, Profile
import json

# Available character skins
AVAILABLE_SKINS = [
    '001', '002', '003', '004', '005', '006', '007', '008', '009',
    '010', '011', '012', '013', '014', '015', '016', '017', '018',
    '019', '020', '021', '022', '023', '024', '025', '026', '027',
    '028', '029', '030', '031', '032', '033', '034', '035', '036',
    '037', '038', '039', '040', '041', '042', '043', '044', '045',
    '046', '047', '048', '049', '050', '051', '052', '053', '054',
    '055', '056', '057', '058', '059', '060', '061', '062', '063',
    '064', '065', '066', '067', '068', '069', '070', '071', '072',
    '073', '074', '075', '076', '077', '078', '079', '080', '081',
    '082', '083'
]


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
    
    # Get visited realms
    profile = request.user.profile
    visited_realm_ids = [str(sid) for sid in profile.visited_realms]
    visited_realms = Realm.objects.filter(share_id__in=visited_realm_ids).exclude(owner=request.user)
    
    return render(request, 'app/dashboard.html', {
        'realms': realms,
        'visited_realms': visited_realms
    })


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


@login_required
def profile(request):
    """User profile page with skin selection"""
    return render(request, 'profile/profile.html', {
        'skins': AVAILABLE_SKINS,
        'current_skin': request.user.profile.skin
    })


@login_required
def edit_realm(request, realm_id):
    """Map editor page"""
    import json
    realm = get_object_or_404(Realm, id=realm_id, owner=request.user)
    return render(request, 'editor/editor.html', {
        'realm': realm,
        'map_data_json': json.dumps(realm.map_data)
    })


@login_required
@require_http_methods(["POST"])
def save_realm_map(request, realm_id):
    """Save map data from editor"""
    realm = get_object_or_404(Realm, id=realm_id, owner=request.user)
    try:
        data = json.loads(request.body)
        realm.map_data = data['map_data']
        realm.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def delete_realm(request, realm_id):
    """Delete a realm"""
    realm = get_object_or_404(Realm, id=realm_id, owner=request.user)
    realm.delete()
    return JsonResponse({'success': True})


@login_required
@require_http_methods(["POST"])
def toggle_realm_privacy(request, realm_id):
    """Toggle only_owner flag"""
    realm = get_object_or_404(Realm, id=realm_id, owner=request.user)
    realm.only_owner = not realm.only_owner
    realm.save()
    return JsonResponse({'success': True, 'only_owner': realm.only_owner})


@login_required
def join_by_share_id(request, share_id):
    """Join realm via share link"""
    realm = get_object_or_404(Realm, share_id=share_id)
    # Add to visited_realms if not owner
    if realm.owner != request.user:
        profile = request.user.profile
        if str(share_id) not in profile.visited_realms:
            profile.visited_realms.append(str(share_id))
            profile.save()
    return redirect('play', realm_id=realm.id)


@login_required
def intro(request, realm_id):
    """Intro screen before entering game"""
    realm = get_object_or_404(Realm, id=realm_id)
    return render(request, 'play/intro.html', {
        'realm': realm,
        'skin': request.user.profile.skin
    })
