from channels.generic.websocket import AsyncWebsocketConsumer
import json
import uuid
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from .models import Realm, Profile


class SessionManager:
    """Manages all active game sessions"""
    def __init__(self):
        self.sessions = {}
        self.player_id_to_realm_id = {}
        self.channel_name_to_player_id = {}
    
    def create_session(self, realm_id, map_data):
        if realm_id not in self.sessions:
            self.sessions[realm_id] = Session(realm_id, map_data)
    
    def get_session(self, realm_id):
        return self.sessions.get(realm_id)
    
    def get_player_session(self, user_id):
        realm_id = self.player_id_to_realm_id.get(user_id)
        if realm_id:
            return self.sessions.get(realm_id)
        return None
    
    def add_player_to_session(self, channel_name, realm_id, user_id, username, skin):
        self.sessions[realm_id].add_player(channel_name, user_id, username, skin)
        self.player_id_to_realm_id[user_id] = realm_id
        self.channel_name_to_player_id[channel_name] = user_id
    
    def logout_player(self, user_id):
        realm_id = self.player_id_to_realm_id.get(user_id)
        if not realm_id:
            return False
        
        session = self.sessions.get(realm_id)
        if session:
            player = session.get_player(user_id)
            if player:
                del self.channel_name_to_player_id[player['channel_name']]
                session.remove_player(user_id)
        
        del self.player_id_to_realm_id[user_id]
        return True
    
    def logout_by_channel_name(self, channel_name):
        user_id = self.channel_name_to_player_id.get(channel_name)
        if user_id:
            return self.logout_player(user_id)
        return False


class Session:
    """Represents a single game realm session"""
    def __init__(self, realm_id, map_data):
        self.realm_id = realm_id
        self.map_data = map_data
        self.players = {}
        self.player_rooms = {}
        self.player_positions = {}
        
        # Initialize room tracking
        for i in range(len(map_data['rooms'])):
            self.player_rooms[i] = set()
            self.player_positions[i] = {}
    
    def add_player(self, channel_name, user_id, username, skin):
        # Remove existing player if reconnecting
        self.remove_player(user_id)
        
        spawn = self.map_data['spawnpoint']
        spawn_room = spawn['roomIndex']
        spawn_x = spawn['x']
        spawn_y = spawn['y']
        
        player = {
            'uid': user_id,
            'username': username,
            'x': spawn_x,
            'y': spawn_y,
            'room': spawn_room,
            'channel_name': channel_name,
            'skin': skin,
            'proximity_id': None
        }
        
        self.players[user_id] = player
        self.player_rooms[spawn_room].add(user_id)
        
        coord_key = f"{spawn_x}, {spawn_y}"
        if coord_key not in self.player_positions[spawn_room]:
            self.player_positions[spawn_room][coord_key] = set()
        self.player_positions[spawn_room][coord_key].add(user_id)
    
    def remove_player(self, user_id):
        if user_id not in self.players:
            return
        
        player = self.players[user_id]
        self.player_rooms[player['room']].discard(user_id)
        
        coord_key = f"{player['x']}, {player['y']}"
        if coord_key in self.player_positions[player['room']]:
            self.player_positions[player['room']][coord_key].discard(user_id)
        
        del self.players[user_id]
    
    def get_player(self, user_id):
        return self.players.get(user_id)
    
    def get_players_in_room(self, room_index):
        return [self.players[uid] for uid in self.player_rooms.get(room_index, set())]
    
    def get_player_count(self):
        return len(self.players)
    
    def move_player(self, user_id, x, y):
        if user_id not in self.players:
            return []
        
        player = self.players[user_id]
        room = player['room']
        
        # Remove from old position
        old_coord = f"{player['x']}, {player['y']}"
        if old_coord in self.player_positions[room]:
            self.player_positions[room][old_coord].discard(user_id)
        
        # Update position
        player['x'] = x
        player['y'] = y
        
        # Add to new position
        new_coord = f"{x}, {y}"
        if new_coord not in self.player_positions[room]:
            self.player_positions[room][new_coord] = set()
        self.player_positions[room][new_coord].add(user_id)
        
        # Update proximity
        return self.set_proximity_ids_with_player(user_id)
    
    def change_room(self, user_id, room_index, x, y):
        if user_id not in self.players:
            return []
        
        player = self.players[user_id]
        old_room = player['room']
        
        # Remove from old room
        self.player_rooms[old_room].discard(user_id)
        old_coord = f"{player['x']}, {player['y']}"
        if old_coord in self.player_positions[old_room]:
            self.player_positions[old_room][old_coord].discard(user_id)
        
        # Add to new room
        player['room'] = room_index
        self.player_rooms[room_index].add(user_id)
        
        # Move to position in new room
        return self.move_player(user_id, x, y)
    
    def set_proximity_ids_with_player(self, user_id):
        """Calculate proximity IDs for video chat"""
        player = self.players[user_id]
        proximity_tiles = self._get_proximity_tiles(player['x'], player['y'])
        changed_players = set()
        original_proximity_id = player['proximity_id']
        other_players_exist = False
        
        for tile in proximity_tiles:
            players_in_tile = self.player_positions[player['room']].get(tile, set())
            
            for other_uid in players_in_tile:
                if other_uid == user_id:
                    continue
                
                other_players_exist = True
                other_player = self.players[other_uid]
                
                if other_player['proximity_id'] is None:
                    if player['proximity_id'] is None:
                        player['proximity_id'] = str(uuid.uuid4())
                        if player['proximity_id'] != original_proximity_id:
                            changed_players.add(user_id)
                    
                    other_player['proximity_id'] = player['proximity_id']
                    changed_players.add(other_uid)
                elif player['proximity_id'] != other_player['proximity_id']:
                    player['proximity_id'] = other_player['proximity_id']
                    if player['proximity_id'] != original_proximity_id:
                        changed_players.add(user_id)
        
        if not other_players_exist:
            player['proximity_id'] = None
            if original_proximity_id is not None:
                changed_players.add(user_id)
        
        return list(changed_players)
    
    def _get_proximity_tiles(self, x, y, range_val=3):
        """Get tiles within proximity range"""
        tiles = []
        for dx in range(-range_val, range_val + 1):
            for dy in range(-range_val, range_val + 1):
                tiles.append(f"{x + dx}, {y + dy}")
        return tiles


# Global session manager
session_manager = SessionManager()


class GameConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for game interactions"""
    
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return
        
        self.user_id = str(self.user.id)
        await self.accept()
    
    async def disconnect(self, close_code):
        if hasattr(self, 'realm_group_name'):
            await self.channel_layer.group_discard(
                self.realm_group_name,
                self.channel_name
            )
        
        # Logout player
        session = session_manager.get_player_session(self.user_id)
        if session:
            # Notify others in room
            player = session.get_player(self.user_id)
            if player:
                room_players = session.get_players_in_room(player['room'])
                for p in room_players:
                    if p['uid'] != self.user_id:
                        await self.channel_layer.send(
                            p['channel_name'],
                            {
                                'type': 'player_left_room',
                                'uid': self.user_id
                            }
                        )
        
        session_manager.logout_by_channel_name(self.channel_name)
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            event_type = data.get('type')
            
            if event_type == 'joinRealm':
                await self.join_realm(data)
            elif event_type == 'movePlayer':
                await self.move_player(data)
            elif event_type == 'teleport':
                await self.teleport(data)
            elif event_type == 'changedSkin':
                await self.changed_skin(data)
            elif event_type == 'sendMessage':
                await self.send_message(data)
        
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))
    
    @sync_to_async
    def get_realm_data(self, realm_id):
        try:
            realm = Realm.objects.get(id=realm_id)
            return realm.map_data, realm.owner_id, realm.only_owner
        except Realm.DoesNotExist:
            return None, None, None
    
    @sync_to_async
    def get_user_skin(self):
        try:
            return self.user.profile.skin
        except:
            return '009'
    
    async def join_realm(self, data):
        realm_id = str(data.get('realmId'))
        
        # Get realm data
        map_data, owner_id, only_owner = await self.get_realm_data(realm_id)
        if not map_data:
            await self.send(text_data=json.dumps({
                'type': 'failedToJoinRoom',
                'reason': 'Space not found.'
            }))
            return
        
        # Check if full
        session = session_manager.get_session(realm_id)
        if session and session.get_player_count() >= 30:
            await self.send(text_data=json.dumps({
                'type': 'failedToJoinRoom',
                'reason': "Space is full. It's 30 players max."
            }))
            return
        
        # Create session if doesn't exist
        if not session:
            session_manager.create_session(realm_id, map_data)
        
        # Get user skin
        skin = await self.get_user_skin()
        
        # Add player to session
        session_manager.add_player_to_session(
            self.channel_name,
            realm_id,
            self.user_id,
            self.user.username,
            skin
        )
        
        session = session_manager.get_session(realm_id)
        player = session.get_player(self.user_id)
        
        # Join realm group
        self.realm_group_name = f"realm_{realm_id}"
        await self.channel_layer.group_add(
            self.realm_group_name,
            self.channel_name
        )
        
        # Send joined confirmation
        await self.send(text_data=json.dumps({
            'type': 'joinedRealm',
            'player': player,
            'players': session.get_players_in_room(player['room'])
        }))
        
        # Notify others in room
        room_players = session.get_players_in_room(player['room'])
        for p in room_players:
            if p['uid'] != self.user_id:
                await self.channel_layer.send(
                    p['channel_name'],
                    {
                        'type': 'player_joined_room',
                        'player': player
                    }
                )
    
    async def move_player(self, data):
        x = data.get('x')
        y = data.get('y')
        
        session = session_manager.get_player_session(self.user_id)
        if not session:
            return
        
        player = session.get_player(self.user_id)
        if not player:
            return
        
        # Update position
        changed_players = session.move_player(self.user_id, x, y)
        
        # Notify others in room
        room_players = session.get_players_in_room(player['room'])
        for p in room_players:
            if p['uid'] != self.user_id:
                await self.channel_layer.send(
                    p['channel_name'],
                    {
                        'type': 'player_moved',
                        'uid': self.user_id,
                        'x': x,
                        'y': y
                    }
                )
        
        # Send proximity updates
        for uid in changed_players:
            changed_player = session.get_player(uid)
            if changed_player:
                await self.channel_layer.send(
                    changed_player['channel_name'],
                    {
                        'type': 'proximity_update',
                        'proximity_id': changed_player['proximity_id']
                    }
                )
    
    async def teleport(self, data):
        room_index = data.get('roomIndex')
        x = data.get('x')
        y = data.get('y')
        
        session = session_manager.get_player_session(self.user_id)
        if not session:
            return
        
        player = session.get_player(self.user_id)
        if not player:
            return
        
        old_room = player['room']
        
        if old_room != room_index:
            # Notify old room players
            old_room_players = session.get_players_in_room(old_room)
            for p in old_room_players:
                if p['uid'] != self.user_id:
                    await self.channel_layer.send(
                        p['channel_name'],
                        {
                            'type': 'player_left_room',
                            'uid': self.user_id
                        }
                    )
            
            # Change room
            changed_players = session.change_room(self.user_id, room_index, x, y)
            
            # Notify new room players
            new_room_players = session.get_players_in_room(room_index)
            for p in new_room_players:
                if p['uid'] != self.user_id:
                    await self.channel_layer.send(
                        p['channel_name'],
                        {
                            'type': 'player_joined_room',
                            'player': player
                        }
                    )
            
            # Send proximity updates
            for uid in changed_players:
                changed_player = session.get_player(uid)
                if changed_player:
                    await self.channel_layer.send(
                        changed_player['channel_name'],
                        {
                            'type': 'proximity_update',
                            'proximity_id': changed_player['proximity_id']
                        }
                    )
        else:
            # Same room teleport
            changed_players = session.move_player(self.user_id, x, y)
            
            # Notify others
            room_players = session.get_players_in_room(room_index)
            for p in room_players:
                if p['uid'] != self.user_id:
                    await self.channel_layer.send(
                        p['channel_name'],
                        {
                            'type': 'player_teleported',
                            'uid': self.user_id,
                            'x': x,
                            'y': y
                        }
                    )
            
            # Send proximity updates
            for uid in changed_players:
                changed_player = session.get_player(uid)
                if changed_player:
                    await self.channel_layer.send(
                        changed_player['channel_name'],
                        {
                            'type': 'proximity_update',
                            'proximity_id': changed_player['proximity_id']
                        }
                    )
    
    async def changed_skin(self, data):
        skin = data.get('skin')
        
        session = session_manager.get_player_session(self.user_id)
        if not session:
            return
        
        player = session.get_player(self.user_id)
        if not player:
            return
        
        player['skin'] = skin
        
        # Notify others in room
        room_players = session.get_players_in_room(player['room'])
        for p in room_players:
            if p['uid'] != self.user_id:
                await self.channel_layer.send(
                    p['channel_name'],
                    {
                        'type': 'player_changed_skin',
                        'uid': self.user_id,
                        'skin': skin
                    }
                )
    
    async def send_message(self, data):
        message = data.get('message', '').strip()
        
        if not message or len(message) > 300:
            return
        
        session = session_manager.get_player_session(self.user_id)
        if not session:
            return
        
        player = session.get_player(self.user_id)
        if not player:
            return
        
        # Notify others in room
        room_players = session.get_players_in_room(player['room'])
        for p in room_players:
            await self.channel_layer.send(
                p['channel_name'],
                {
                    'type': 'receive_message',
                    'uid': self.user_id,
                    'username': player['username'],
                    'message': message
                }
            )
    
    # Channel layer event handlers
    async def player_joined_room(self, event):
        await self.send(text_data=json.dumps({
            'type': 'playerJoinedRoom',
            'player': event['player']
        }))
    
    async def player_left_room(self, event):
        await self.send(text_data=json.dumps({
            'type': 'playerLeftRoom',
            'uid': event['uid']
        }))
    
    async def player_moved(self, event):
        await self.send(text_data=json.dumps({
            'type': 'playerMoved',
            'uid': event['uid'],
            'x': event['x'],
            'y': event['y']
        }))
    
    async def player_teleported(self, event):
        await self.send(text_data=json.dumps({
            'type': 'playerTeleported',
            'uid': event['uid'],
            'x': event['x'],
            'y': event['y']
        }))
    
    async def player_changed_skin(self, event):
        await self.send(text_data=json.dumps({
            'type': 'playerChangedSkin',
            'uid': event['uid'],
            'skin': event['skin']
        }))
    
    async def receive_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'receiveMessage',
            'uid': event['uid'],
            'username': event['username'],
            'message': event['message']
        }))
    
    async def proximity_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'proximityUpdate',
            'proximityId': event['proximity_id']
        }))
