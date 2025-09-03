Live Logging WebSocket (Alpha)

- Raw WebSocket endpoint: `ws://<host>:5010` (configurable via `LOG_WS_PORT`)
- Stream: JSON events — `waldo_log`, `waldo_state`, `api`, `cooldown`, `stats`
- Generate events:
  - Single: `POST http://<host>:5002/analyze`
  - Continuous: `POST http://<host>:5002/monitor/start`

Example (websocat):
- `websocat ws://<host>:5010`

Example (Node):
- `npm i ws`
- `const ws = new (require('ws'))('ws://<host>:5010'); ws.on('message', m => console.log(m.toString()));`
