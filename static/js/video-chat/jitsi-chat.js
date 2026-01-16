// Jitsi Meet video chat integration (replaces Agora)
class JitsiChat {
    constructor() {
        this.api = null;
        this.currentChannel = '';
        this.cameraEnabled = false;
        this.micEnabled = false;
        this.channelTimeout = null;
        this.domain = 'meet.jit.si'; // Use public Jitsi server or configure your own
    }

    async joinChannel(channel, uid, realmId) {
        if (this.channelTimeout) {
            clearTimeout(this.channelTimeout);
        }

        this.channelTimeout = setTimeout(async () => {
            const uniqueChannelId = this.createUniqueChannelId(realmId, channel);
            
            if (uniqueChannelId === this.currentChannel && this.api) {
                return; // Already in this channel
            }

            // Leave current channel if any
            if (this.api) {
                await this.leaveChannel();
            }

            this.currentChannel = uniqueChannelId;
            
            // Create Jitsi Meet room
            const options = {
                roomName: uniqueChannelId,
                width: '100%',
                height: '100%',
                parentNode: document.querySelector('#local-video'),
                configOverwrite: {
                    startWithAudioMuted: !this.micEnabled,
                    startWithVideoMuted: !this.cameraEnabled,
                    prejoinPageEnabled: false,
                    disableDeepLinking: true
                },
                interfaceConfigOverwrite: {
                    TOOLBAR_BUTTONS: [],
                    SHOW_JITSI_WATERMARK: false,
                    SHOW_WATERMARK_FOR_GUESTS: false,
                    MOBILE_APP_PROMO: false
                },
                userInfo: {
                    displayName: window.REALM_DATA.username
                }
            };

            this.api = new JitsiMeetExternalAPI(this.domain, options);

            // Handle remote participants
            this.api.addEventListener('participantJoined', (event) => {
                console.log('Participant joined:', event);
                this.onParticipantJoined(event);
            });

            this.api.addEventListener('participantLeft', (event) => {
                console.log('Participant left:', event);
                this.onParticipantLeft(event);
            });

            this.api.addEventListener('videoConferenceJoined', (event) => {
                console.log('Joined video conference:', event);
            });

            // Apply current audio/video state
            if (!this.cameraEnabled) {
                this.api.executeCommand('toggleVideo');
            }
            if (!this.micEnabled) {
                this.api.executeCommand('toggleAudio');
            }
        }, 1000);
    }

    async leaveChannel() {
        if (this.channelTimeout) {
            clearTimeout(this.channelTimeout);
        }

        this.channelTimeout = setTimeout(() => {
            if (this.currentChannel === '') {
                return;
            }

            if (this.api) {
                this.api.dispose();
                this.api = null;
            }

            this.currentChannel = '';
            
            // Clear remote video containers
            const remoteVideos = document.querySelector('#remote-videos');
            if (remoteVideos) {
                remoteVideos.innerHTML = '';
            }
        }, 1000);
    }

    async toggleCamera() {
        this.cameraEnabled = !this.cameraEnabled;
        
        if (this.api) {
            this.api.executeCommand('toggleVideo');
        }

        return !this.cameraEnabled; // Return true if camera is OFF
    }

    async toggleMicrophone() {
        this.micEnabled = !this.micEnabled;
        
        if (this.api) {
            this.api.executeCommand('toggleAudio');
        }

        return !this.micEnabled; // Return true if mic is muted
    }

    createUniqueChannelId(realmId, channel) {
        // Create a unique channel ID based on realm and channel
        // This ensures each proximity group or private area has its own video room
        return `gather-${realmId}-${channel}`.replace(/[^a-zA-Z0-9-]/g, '_');
    }

    onParticipantJoined(event) {
        const participantId = event.id;
        const remoteVideos = document.querySelector('#remote-videos');
        
        if (!remoteVideos) return;

        // Create container for remote video
        const videoContainer = document.createElement('div');
        videoContainer.id = `participant-${participantId}`;
        videoContainer.className = 'w-48 h-36 bg-gray-800 rounded-lg overflow-hidden';
        remoteVideos.appendChild(videoContainer);

        window.signal.emit('user-joined', { id: participantId });
    }

    onParticipantLeft(event) {
        const participantId = event.id;
        const videoContainer = document.querySelector(`#participant-${participantId}`);
        
        if (videoContainer) {
            videoContainer.remove();
        }

        window.signal.emit('user-left', { id: participantId });
    }
}

const jitsiChat = new JitsiChat();
window.jitsiChat = jitsiChat;
