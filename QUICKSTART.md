# Quick Start Guide - Django Gather

## 🚀 Get Started in 3 Minutes

### 1. Install & Setup
```bash
# Clone the repository
git clone https://github.com/pedrohusky/Django-Gather.git
cd Django-Gather

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate
```

### 2. Run the Server
```bash
python manage.py runserver
```

Visit: **http://localhost:8000/**

### 3. Create Your First Space

1. **Sign Up** - Create an account at http://localhost:8000/signup/
2. **Login** - Sign in with your credentials
3. **Create Space** - Click "Create New Space" on the dashboard
4. **Enter Space** - Click "Enter" to join your space
5. **Share** - Click "Share" to copy the invite link

## 🎮 How to Use

### Basic Controls
- **Movement**: Click to move (or use WASD/Arrow keys when implemented)
- **Camera**: Click 📷 Camera button to enable/disable video
- **Microphone**: Click 🎤 Mic button to mute/unmute audio
- **Chat**: Type messages in the chat box and click Send

### Multiplayer
- Share your space's link with others
- Players within 3 tiles automatically join video chat
- Up to 30 players per space

### Video Chat (Jitsi)
- Proximity-based: Get close to others to start video chat
- Private areas: Designated zones for private conversations
- Free and open-source (uses public Jitsi server by default)

## 🔧 Admin Panel

Create a superuser to access the Django admin:

```bash
python manage.py createsuperuser
```

Visit: **http://localhost:8000/admin/**

Manage:
- Users and profiles
- Realms/spaces
- View all data

## 📝 Configuration

### Change Default Skin
In Django admin or shell:
```python
from core.models import Profile
profile = Profile.objects.get(user__username='your_username')
profile.skin = '042'  # Change to any character 001-083
profile.save()
```

### Use Your Own Jitsi Server
Edit `static/js/video-chat/jitsi-chat.js`:
```javascript
this.domain = 'your-jitsi-server.com';
```

### Production Setup
1. Set `DEBUG = False` in `gather/settings.py`
2. Configure `ALLOWED_HOSTS`
3. Use PostgreSQL instead of SQLite
4. Set up Redis for WebSocket channels
5. Run with Daphne or Gunicorn

```bash
# With Daphne
daphne -b 0.0.0.0 -p 8000 gather.asgi:application
```

## 🐛 Troubleshooting

### "Address already in use" error
```bash
# Find process using port 8000
ps aux | grep runserver
# Kill the process
kill <PID>
```

### Database issues
```bash
# Reset database
rm db.sqlite3
python manage.py migrate
```

### Static files not loading
```bash
# Collect static files
python manage.py collectstatic
```

## 📚 Next Steps

- Read the full README.md for detailed documentation
- Explore the Django admin panel
- Customize your space layout
- Invite friends to test multiplayer
- Deploy to production (Heroku, DigitalOcean, etc.)

## 🤝 Need Help?

- Check the main README.md
- Review code comments
- Test with `python test_functionality.py`

Enjoy your Django Gather experience! 🎉
