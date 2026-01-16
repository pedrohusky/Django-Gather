#!/usr/bin/env python3
"""
Test script to verify Django Gather functionality
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gather.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Profile, Realm

def test_models():
    """Test that models are working correctly"""
    print("Testing models...")
    
    # Test user creation
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    print(f"✓ Created user: {user.username}")
    
    # Test profile auto-creation
    profile = Profile.objects.get(user=user)
    print(f"✓ Profile auto-created with skin: {profile.skin}")
    
    # Test realm creation
    realm = Realm.objects.create(
        owner=user,
        name='Test Space',
        map_data={
            'spawnpoint': {'roomIndex': 0, 'x': 5, 'y': 5},
            'rooms': [{
                'name': 'Main Room',
                'tilemap': {}
            }]
        }
    )
    print(f"✓ Created realm: {realm.name} (ID: {realm.id})")
    print(f"  Share ID: {realm.share_id}")
    
    # Cleanup
    realm.delete()
    user.delete()
    print("✓ Cleanup completed")
    
    print("\n✅ All model tests passed!")

def test_websocket_routing():
    """Test that WebSocket routing is configured"""
    print("\nTesting WebSocket configuration...")
    
    from core.routing import websocket_urlpatterns
    print(f"✓ WebSocket routes configured: {len(websocket_urlpatterns)} route(s)")
    
    from core.consumers import GameConsumer
    print("✓ GameConsumer class imported successfully")
    
    print("\n✅ WebSocket configuration tests passed!")

def test_views():
    """Test that views are accessible"""
    print("\nTesting views...")
    
    from django.test import Client
    client = Client()
    
    # Test home page
    response = client.get('/')
    print(f"✓ Home page: Status {response.status_code}")
    assert response.status_code == 200, "Home page should return 200"
    
    # Test signin page
    response = client.get('/signin/')
    print(f"✓ Sign in page: Status {response.status_code}")
    assert response.status_code == 200, "Sign in page should return 200"
    
    # Test signup page
    response = client.get('/signup/')
    print(f"✓ Sign up page: Status {response.status_code}")
    assert response.status_code == 200, "Sign up page should return 200"
    
    print("\n✅ All view tests passed!")

if __name__ == '__main__':
    print("=" * 60)
    print("Django Gather - Functionality Tests")
    print("=" * 60)
    
    try:
        test_models()
        test_websocket_routing()
        test_views()
        
        print("\n" + "=" * 60)
        print("🎉 All tests passed successfully!")
        print("=" * 60)
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
