# Pi ↔ Server Ingest Sync Note

Context and Current State
- Goal: Minimal Pi → Server ingest over a single WebSocket; Server handles central visualizer (overlays, publishing to site).
- Viewer:
  - Fallback (no UDP): https://dev.thegonzalez.design/?fallback=1
  - WebRTC (lower latency): https://dev.thegonzalez.design/?relay=1&turn=dev.thegonzalez.design
- Ingest (live):
  - WebSocket: `wss://dev.thegonzalez.design/ws/ingest/{source_id}?token=YOUR_TOKEN`
  - Optional first message (JSON): `{ "type":"hello","w":1280,"h":720,"fmt":"jpeg" }`
  - Then: binary JPEG frames
  - Auth: token validated against `WV_INGEST_TOKEN` on Server
- Publishing bus: Server publishes incoming ingest frames to the same bus used by fallback MJPEG and WebRTC.

Pi-Side Implementation
- A lightweight ingest publisher is integrated with the Pi’s monitor loop.
  - Env toggles:
    - `INGEST_ENABLED=true|false`
    - `INGEST_WS_URL=wss://dev.thegonzalez.design/ws/ingest/{source_id}?token=YOUR_TOKEN`
  - Operation:
    - Sends hello JSON with camera w/h, then enqueues JPEG bytes for each processed frame.
    - Non‑blocking; reconnects on errors; never disrupts the vision pipeline.
  - Defaults:
    - Resolution: camera’s setting (can constrain to 720p).
    - JPEG Q: ~80 (configurable; 70 recommended for lower bandwidth per server guidance).
    - FPS: ~10–20 FPS typical from monitor loop (can throttle explicitly if requested).

Server Expectations and Contracts
- WS ingest endpoint:
  - Accepts optional hello and binary JPEG frames.
  - Auth via `?token`; on invalid token → 401 + close.
- Publishing:
  - Ingest frames forwarded to the site stream bus; fallback viewer should render immediately.
  - If per‑source routing is added later, expose `/stream/{source_id}.mjpeg` and viewer `?source={source_id}`.

Error Handling & Backoff
- Pi: reconnect after short backoff on any WS error; drop frames if queue full (non‑blocking enqueue).
- Server: 401 (invalid token); 1009 (message too big) if enforced; Pi will adjust size/quality/FPS on request.

Security & Auth
- Token: provision `WV_INGEST_TOKEN` on Server and provide securely for Pi’s `.env`.
- TLS: Pi uses `wss://`; assumes valid cert chain on `dev.thegonzalez.design`.

Performance & Limits
- Initial target: 1280×720 @ ~12–15 FPS, JPEG Q=70–80.
- If needed, we can throttle to a target FPS or reduce quality/size.
- Please confirm max acceptable WS message size so we cap JPEG size accordingly.

Ops & Debugging
- Diagnostics on the webpage show WS status; fallback should render ingest frames.
- Logs: Server should show ingest connections, hello JSON, frame counts.

Aligned Decisions
- Pi will NOT publish WebRTC; only JPEG over WS to Server, per current plan.
- Overlays drawn centrally on Server.

Questions for Server
1) Token provisioning: confirm `WV_INGEST_TOKEN` set (option for per‑source tokens)?
2) Source identity: do you want per‑source viewing (e.g., `/stream/{source_id}.mjpeg` and viewer `?source=`)?
3) Size limits: what max WS message size should we target?
4) Backoff preference: is a simple retry (2s, with minor increase) acceptable?
5) FPS cap: do you want explicit throttle (e.g., 12–15 FPS), or is “every processed frame” acceptable?
6) Metadata: if you plan to support other formats or per‑frame meta, share the schema you prefer (we can add minimal JSON meta periodically).

Questions for Pi (self‑check)
1) Confirm `.env` contains: `INGEST_ENABLED=true` and `INGEST_WS_URL=...` (with `{source_id}` and token).
2) Confirm fallback viewer renders frames after start.
3) Adjust JPEG Q/FPS if server signals bandwidth constraints.

