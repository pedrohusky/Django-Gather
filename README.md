# Gather Clone - Django Full-Stack Edition

[Watch the original demo](https://www.youtube.com/watch?v=AnhsC7Fmt20)

A complete Django full-stack rewrite of the Gather.town clone, featuring fully customizable spaces and seamless proximity-based video chat using Jitsi Meet.

## Major Changes from Original

This version has been completely refactored from the original Next.js/React/Supabase/Agora stack to:

### Old Stack
- **Frontend**: Next.js + React + TypeScript + TailwindCSS + Pixi.js
- **Backend**: Node.js + Express + Socket.io
- **Database**: Supabase (PostgreSQL + Auth)
- **Video Chat**: Agora SDK
- **Authentication**: Supabase Auth (Google OAuth)

### New Stack
- **Backend**: Django + Django Channels (WebSockets)
- **Frontend**: Django Templates + JavaScript (vanilla) + TailwindCSS
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **Video Chat**: Jitsi Meet (lib-jitsi-meet)
- **Authentication**: Django Auth (username/password)
- **Real-time**: Django Channels with WebSockets
- **Game Engine**: Pixi.js (maintained)

## Features

The app includes all core features:

- ✅ **Customizable spaces** using tilesets
- ✅ **Proximity video chat** with Jitsi Meet
- ✅ **Private area video chat** 
- ✅ **Multiplayer networking** via WebSockets
- ✅ **Tile-based movement**
- ✅ **Real-time chat messaging**
- ✅ **User authentication** (registration/login)
- ✅ **Realm management** (create/join spaces)

## Installation

### Prerequisites
- Python 3.12+
- pip

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/pedrohusky/Django-Gather.git
cd Django-Gather
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run migrations**
```bash
python manage.py migrate
```

4. **Create a superuser (optional, for admin access)**
```bash
python manage.py createsuperuser
```

5. **Run the development server**
```bash
python manage.py runserver
```

6. **Access the application**
- Main site: http://localhost:8000/
- Admin panel: http://localhost:8000/admin/

## Project Structure

```
Django-Gather/
├── manage.py                  # Django management script
├── requirements.txt           # Python dependencies
├── gather/                    # Django project configuration
│   ├── settings.py           # Django settings
│   ├── urls.py               # Main URL routing
│   ├── asgi.py               # ASGI config for Channels
│   └── wsgi.py               # WSGI config
├── core/                      # Main Django app
│   ├── models.py             # Profile & Realm models
│   ├── views.py              # View functions
│   ├── forms.py              # Authentication forms
│   ├── urls.py               # App URL routing
│   ├── consumers.py          # WebSocket consumers
│   ├── routing.py            # WebSocket routing
│   └── admin.py              # Admin configuration
├── templates/                 # Django templates
│   ├── base.html             # Base template with navbar
│   ├── home.html             # Landing page
│   ├── auth/                 # Authentication templates
│   │   ├── signin.html
│   │   └── signup.html
│   ├── app/                  # Application templates
│   │   └── dashboard.html    # Realm management
│   └── play/                 # Game templates
│       └── play.html         # Game interface
├── static/                    # Static files
│   ├── js/
│   │   ├── signal.js         # Event emitter
│   │   ├── main.js           # Game initialization
│   │   ├── pixi/             # Pixi.js game logic
│   │   ├── video-chat/       # Jitsi integration
│   │   └── websocket/        # WebSocket client
│   └── sprites/              # Game assets
│       ├── characters/
│       └── spritesheets/
└── db.sqlite3                # SQLite database (dev)
```

## How It Works

### Authentication
- Simple username/password authentication using Django's built-in auth system
- Users register, login, and manage their profile (including avatar skin selection)

### Realms (Spaces)
- Users can create multiple realms/spaces with custom names
- Each realm has a unique share ID for inviting others
- Realms store map data (rooms, tiles, spawn points) in JSON format

### Multiplayer
- Real-time multiplayer via Django Channels (WebSockets)
- Server manages player sessions, positions, and proximity calculations
- Events: joinRealm, movePlayer, teleport, changedSkin, sendMessage

### Video Chat
- Jitsi Meet integration for video/audio communication
- Automatic channel switching based on proximity
- Players within 3 tiles of each other join the same video room
- Private areas can have dedicated video channels

### Frontend
- Pixi.js for game rendering (character sprites, tiles, animations)
- Vanilla JavaScript for game logic
- TailwindCSS for UI styling

## Development

### Database Models

**Profile**
- One-to-one with Django User
- Fields: skin (character appearance), visited_realms (JSON array)

**Realm**
- Owner (ForeignKey to User)
- Fields: name, share_id (UUID), map_data (JSON), only_owner (boolean)

### WebSocket Events

**Client → Server:**
- `joinRealm` - Join a realm/space
- `movePlayer` - Update player position
- `teleport` - Teleport to different room/location
- `changedSkin` - Change character skin
- `sendMessage` - Send chat message

**Server → Client:**
- `joinedRealm` - Confirmation of join
- `playerJoinedRoom` - Another player joined
- `playerLeftRoom` - Player disconnected
- `playerMoved` - Player position update
- `receiveMessage` - Chat message received
- `proximityUpdate` - Video chat proximity group changed

## Configuration

### Production Setup

For production deployment:

1. **Update `gather/settings.py`:**
   - Set `DEBUG = False`
   - Configure `ALLOWED_HOSTS`
   - Use PostgreSQL instead of SQLite
   - Set up Redis for channel layers

2. **Channel Layers (Redis)**
```python
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}
```

3. **Static Files**
```bash
python manage.py collectstatic
```

4. **Use gunicorn/daphne for production**
```bash
daphne -b 0.0.0.0 -p 8000 gather.asgi:application
```

## Video Chat Configuration

By default, the app uses the public Jitsi Meet server (`meet.jit.si`). For production:

1. **Self-hosted Jitsi** (recommended for better performance)
   - Install Jitsi Meet on your server
   - Update `jitsi-chat.js` domain to your Jitsi server

2. **Custom Jitsi Domain**
```javascript
// In static/js/video-chat/jitsi-chat.js
this.domain = 'your-jitsi-server.com';
```

## API Endpoints

- `POST /api/realms/create/` - Create new realm
- `GET /api/realms/<id>/` - Get realm data
- `POST /api/profile/update/` - Update user profile

## WebSocket Endpoint

- `ws://localhost:8000/ws/game/` - Game WebSocket connection

## Differences from Original

1. **No Google OAuth** - Simple username/password authentication
2. **No Supabase** - Django ORM with SQLite/PostgreSQL
3. **No Agora SDK** - Jitsi Meet for video chat (free, open-source)
4. **No Next.js/React** - Django templates with vanilla JavaScript
5. **Simplified Pixi.js** - Core game logic without full TypeScript classes

## Contributing

This is a refactored version. For the original project, see: https://github.com/trevorwrightdev/gather-clone

## License

This project maintains the same license as the original Gather Clone project.
