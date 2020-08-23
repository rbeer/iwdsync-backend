# Install

# Websocket API

## /ws/caster/{caster}

  - Requires session (/admin) and logged in user being assigned to Caster with `url_path == {caster}`

### Messages
##### HEARTBEAT
```json
⇧ { "type":"HEARTBEAT", "youtube_time": Number }
```
```json
⇩ { "status": "ok" }
```

Send value of [player.getCurrentTime()](https://developers.google.com/youtube/iframe_api_reference#getCurrentTime) to server and relay value to connected viewers.

---

##### CONTROL

```json
⇧ { "type":"CONTROL", "action": <"PLAY", "PAUSE">}
```
```json
⇩ { "status": "ok" }
```
Send changes to the [player's state](https://developers.google.com/youtube/iframe_api_reference#getPlayerState) to server and relay to connected viewers. Valid values for `action` are `"PLAY"` and `"PAUSE"`.

---

## /ws/viewer/{caster}
##### HEARTBEAT
```json
⇩ { "type":"HEARTBEAT", "youtube_time": Number }
```
Receives `HEARTBEAT` messages whenever caster updates `youtube_time`. Use the value - plus Twitch's broadcaster delay - for [player.seekTo()](https://developers.google.com/youtube/iframe_api_reference#seekTo) to synchronize with the caster.

##### CONTROL
```json
⇩ { "type":"CONTROL", "action": <"PLAY", "PAUSE">}
```
Receives `CONTROL` messages sent by caster. Forward to [player.playVideo|pauseVideo](https://developers.google.com/youtube/iframe_api_reference#playVideo).
