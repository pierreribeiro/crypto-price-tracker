# WebSocket Specification: CryptoTracker Pro

**Date**: 2026-01-09
**Protocol**: WebSocket (Native)
**Implementation**: FastAPI built-in WebSocket support
**Purpose**: Real-time cryptocurrency price updates (FR-013, FR-005: Real-Time Updates)

---

## Overview

This specification defines the WebSocket protocol for real-time price updates in CryptoTracker Pro. The WebSocket connection provides bi-directional communication between client and server for:

- Automatic price updates every 30 seconds (FR-013)
- Instant updates triggered by manual refresh (FR-014)
- Connection state management and error handling
- Pub/sub pattern via Redis for efficient multi-client distribution

---

## Connection

### Endpoint

```
ws://localhost:8000/api/v1/ws/prices
wss://api.cryptotracker.example/v1/ws/prices  (Production with TLS)
```

### Protocol

- **Transport**: WebSocket (Native, RFC 6455)
- **Subprotocol**: None (custom JSON message format)
- **Heartbeat**: 25-second ping/pong interval
- **Reconnection**: Client-side exponential backoff (1s, 2s, 4s, 8s, max 30s)

### Connection Lifecycle

```
Client                          Server
  |                               |
  |--- WebSocket Handshake ------>|
  |<-- 101 Switching Protocols ---|
  |                               |
  |--- subscribe message -------->|
  |<-- subscription_confirmed ----|
  |                               |
  |<-- price_update (30s) --------|
  |<-- price_update (30s) --------|
  |                               |
  |--- ping (25s) --------------->|
  |<-- pong ---------------------|
  |                               |
  |--- unsubscribe -------------->|
  |<-- unsubscribed --------------|
  |                               |
  |--- close -------------------->|
  |<-- close ---------------------|
```

---

## Message Format

All messages use JSON format with `type` field for message discrimination.

### General Message Structure

```typescript
interface WebSocketMessage {
  type: string;           // Message type (snake_case)
  timestamp: string;      // ISO 8601 timestamp
  [key: string]: any;     // Type-specific fields
}
```

---

## Client-to-Server Messages

### 1. Subscribe

Request to start receiving price updates for specific cryptocurrencies or all top 20.

**Message Type**: `subscribe`

```json
{
  "type": "subscribe",
  "timestamp": "2026-01-09T12:30:00Z",
  "cryptocurrencies": ["bitcoin", "ethereum", "cardano"],  // Optional: specific IDs
  "include_sparkline": true                                // Optional: include 7-day data
}
```

**Parameters**:
- `cryptocurrencies` (optional): Array of cryptocurrency IDs to subscribe to. If omitted, subscribes to all top 20.
- `include_sparkline` (optional): Boolean. If `true`, include sparkline data in updates. Default: `false`.

**Response**: Server sends `subscription_confirmed` message.

---

### 2. Unsubscribe

Request to stop receiving price updates.

**Message Type**: `unsubscribe`

```json
{
  "type": "unsubscribe",
  "timestamp": "2026-01-09T12:35:00Z"
}
```

**Response**: Server sends `unsubscribed` message and stops price updates.

---

### 3. Ping

Client-initiated heartbeat to keep connection alive.

**Message Type**: `ping`

```json
{
  "type": "ping",
  "timestamp": "2026-01-09T12:30:00Z"
}
```

**Response**: Server responds with `pong` message immediately.

---

### 4. Refresh Request

Request immediate price refresh (manual refresh button, FR-014).

**Message Type**: `refresh_request`

```json
{
  "type": "refresh_request",
  "timestamp": "2026-01-09T12:30:00Z"
}
```

**Response**: Server immediately fetches latest prices and sends `price_update` message.

---

## Server-to-Client Messages

### 1. Subscription Confirmed

Confirms successful subscription and provides initial data.

**Message Type**: `subscription_confirmed`

```json
{
  "type": "subscription_confirmed",
  "timestamp": "2026-01-09T12:30:00Z",
  "subscribed_to": ["bitcoin", "ethereum", "cardano"],  // or "all" for top 20
  "update_interval_seconds": 30,                        // FR-013: 30-second auto-refresh
  "initial_data": {
    "data": [/* array of Cryptocurrency objects */],
    "metadata": {
      "count": 20,
      "lastUpdated": "2026-01-09T12:30:00Z",
      "dataSource": "coingecko"
    }
  }
}
```

---

### 2. Price Update

Real-time price update for subscribed cryptocurrencies.

**Message Type**: `price_update`

```json
{
  "type": "price_update",
  "timestamp": "2026-01-09T12:31:00Z",
  "data": [
    {
      "id": "bitcoin",
      "symbol": "BTC",
      "name": "Bitcoin",
      "currentPrice": 42350.25,
      "marketCap": 831245678901.23,
      "volume24h": 28456789012.45,
      "priceChange24h": 523.75,
      "priceChangePercent24h": 1.25,
      "sparklineData": [/* optional: array of PriceDataPoint */],
      "rank": 1,
      "lastUpdated": "2026-01-09T12:31:00Z",
      "priceDirection": "up",
      "marketCapCategory": "large"
    }
    /* ... more cryptocurrencies */
  ],
  "metadata": {
    "count": 20,
    "lastUpdated": "2026-01-09T12:31:00Z",
    "dataSource": "coingecko",
    "updateType": "scheduled"  // "scheduled" or "manual"
  }
}
```

**Update Types**:
- `scheduled`: Automatic 30-second refresh (FR-013)
- `manual`: User-triggered refresh (FR-014)

---

### 3. Unsubscribed

Confirms unsubscription and stops updates.

**Message Type**: `unsubscribed`

```json
{
  "type": "unsubscribed",
  "timestamp": "2026-01-09T12:35:00Z",
  "message": "Successfully unsubscribed from price updates"
}
```

---

### 4. Pong

Response to client ping (heartbeat mechanism).

**Message Type**: `pong`

```json
{
  "type": "pong",
  "timestamp": "2026-01-09T12:30:00Z"
}
```

---

### 5. Error

Server error message with actionable information (FR-019).

**Message Type**: `error`

```json
{
  "type": "error",
  "timestamp": "2026-01-09T12:30:00Z",
  "code": "EXTERNAL_API_FAILURE",
  "message": "External API unavailable. Serving cached data.",
  "severity": "warning",  // "warning", "error", "critical"
  "data_staleness": "2 minutes",
  "retry_in_seconds": 60
}
```

**Error Codes**:
- `EXTERNAL_API_FAILURE`: Both CoinGecko and CoinMarketCap unavailable (Edge Case: API unavailability)
- `RATE_LIMIT_EXCEEDED`: API rate limit reached (Edge Case: Rate limiting)
- `INVALID_MESSAGE_FORMAT`: Client sent malformed message
- `SUBSCRIPTION_ERROR`: Unable to process subscription request
- `INTERNAL_SERVER_ERROR`: Unexpected server error

---

### 6. Connection State

Informs client about connection health and data freshness.

**Message Type**: `connection_state`

```json
{
  "type": "connection_state",
  "timestamp": "2026-01-09T12:30:00Z",
  "status": "connected",        // "connected", "degraded", "reconnecting"
  "data_freshness": "fresh",    // "fresh", "stale", "cached"
  "last_successful_update": "2026-01-09T12:30:00Z",
  "cache_age_seconds": 0,
  "external_api_status": {
    "coingecko": "available",   // "available", "unavailable"
    "coinmarketcap": "available"
  }
}
```

---

## Error Handling

### Client-Side Error Handling

**Disconnection**:
1. Detect disconnection via WebSocket `close` or `error` event
2. Display "Disconnected" indicator to user
3. Attempt reconnection with exponential backoff:
   - 1st retry: 1 second
   - 2nd retry: 2 seconds
   - 3rd retry: 4 seconds
   - 4th retry: 8 seconds
   - 5th+ retry: 30 seconds (max)
4. After 5 failed attempts, prompt user to manually refresh

**Stale Data**:
- Display warning indicator when `data_freshness: "stale"` received
- Show last successful update timestamp (FR-015)
- Allow manual refresh (FR-014)

**API Failures**:
- When server sends `error` with `EXTERNAL_API_FAILURE`, display cached data with warning
- Show "Data may be stale" message with timestamp
- Continue attempting automatic updates in background

### Server-Side Error Handling

**External API Failure** (FR-022: CoinGecko → CoinMarketCap fallback):
1. Attempt CoinGecko API request
2. On failure (timeout, 5xx, 429), attempt CoinMarketCap API
3. On both failures:
   - Serve cached data from Redis (if available within 5-minute TTL)
   - Send `error` message with `severity: "warning"`
   - Log error for monitoring

**Rate Limiting** (Edge Case: Rate limiting):
1. Implement request throttling to stay within API limits
2. Use Redis to track request counts per time window
3. When limit approached:
   - Serve cached data
   - Delay next update by calculated cooldown period
   - Send `connection_state` with `status: "degraded"`

**Malformed Data** (Edge Case: Malformed API responses):
1. Validate all incoming API data with data-model validation
2. Filter out invalid entries
3. Log errors for debugging
4. Only send valid cryptocurrency information to clients
5. If all data invalid, send `error` message

---

## Implementation Notes

### Backend (FastAPI)

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List, Dict
import asyncio
import json
from datetime import datetime

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                # Connection broken, will be removed on next disconnect
                pass

manager = ConnectionManager()

@app.websocket("/api/v1/ws/prices")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial subscription confirmation
        await websocket.send_text(json.dumps({
            "type": "subscription_confirmed",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "subscribed_to": "all",
            "update_interval_seconds": 30
        }))

        # Start 30-second update task
        update_task = asyncio.create_task(send_price_updates(websocket))

        # Handle incoming messages
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message["type"] == "ping":
                await websocket.send_text(json.dumps({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }))
            elif message["type"] == "refresh_request":
                # Trigger immediate update
                await send_immediate_update(websocket)
            elif message["type"] == "unsubscribe":
                update_task.cancel()
                await websocket.send_text(json.dumps({
                    "type": "unsubscribed",
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }))
                break

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        # Log error and send error message
        await websocket.send_text(json.dumps({
            "type": "error",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred"
        }))
        manager.disconnect(websocket)

async def send_price_updates(websocket: WebSocket):
    while True:
        await asyncio.sleep(30)  # FR-013: 30-second interval
        # Fetch latest prices from cache or API
        prices = await fetch_cryptocurrency_data()
        await websocket.send_text(json.dumps({
            "type": "price_update",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "data": prices,
            "metadata": {
                "count": len(prices),
                "lastUpdated": datetime.utcnow().isoformat() + "Z",
                "dataSource": "coingecko",
                "updateType": "scheduled"
            }
        }))
```

### Frontend (React)

```typescript
// Custom hook for WebSocket connection management
function useWebSocket(url: string) {
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [connectionState, setConnectionState] = useState<'connecting' | 'connected' | 'disconnected'>('connecting');
  const [prices, setPrices] = useState<Cryptocurrency[]>([]);

  useEffect(() => {
    let socket: WebSocket;
    let reconnectAttempt = 0;
    let reconnectTimeout: NodeJS.Timeout;

    function connect() {
      socket = new WebSocket(url);

      socket.onopen = () => {
        setConnectionState('connected');
        reconnectAttempt = 0;

        // Send subscribe message
        socket.send(JSON.stringify({
          type: 'subscribe',
          timestamp: new Date().toISOString(),
          include_sparkline: true
        }));

        // Start heartbeat
        const heartbeat = setInterval(() => {
          if (socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({
              type: 'ping',
              timestamp: new Date().toISOString()
            }));
          }
        }, 25000); // 25-second heartbeat

        socket.onclose = () => clearInterval(heartbeat);
      };

      socket.onmessage = (event) => {
        const message = JSON.parse(event.data);

        switch (message.type) {
          case 'subscription_confirmed':
            setPrices(message.initial_data.data);
            break;
          case 'price_update':
            setPrices(message.data);
            break;
          case 'error':
            console.error('WebSocket error:', message);
            // Display error to user
            break;
          case 'pong':
            // Heartbeat acknowledged
            break;
        }
      };

      socket.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      socket.onclose = () => {
        setConnectionState('disconnected');
        setWs(null);

        // Exponential backoff reconnection
        const delay = Math.min(1000 * Math.pow(2, reconnectAttempt), 30000);
        reconnectAttempt++;

        reconnectTimeout = setTimeout(() => {
          if (reconnectAttempt <= 5) {
            connect();
          }
        }, delay);
      };

      setWs(socket);
    }

    connect();

    return () => {
      clearTimeout(reconnectTimeout);
      if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({
          type: 'unsubscribe',
          timestamp: new Date().toISOString()
        }));
        socket.close();
      }
    };
  }, [url]);

  const manualRefresh = useCallback(() => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({
        type: 'refresh_request',
        timestamp: new Date().toISOString()
      }));
    }
  }, [ws]);

  return { connectionState, prices, manualRefresh };
}
```

---

## Performance Considerations

1. **Connection Pooling**: Use Redis pub/sub to broadcast updates to all connected clients efficiently
2. **Message Throttling**: Limit message size and frequency to prevent bandwidth saturation
3. **Heartbeat**: 25-second ping/pong interval keeps connection alive without excessive overhead
4. **Reconnection**: Exponential backoff prevents server overload during mass disconnections
5. **Data Compression**: Consider WebSocket compression extension for production (permessage-deflate)

---

## Security Considerations

1. **TLS Required**: Production MUST use `wss://` (WebSocket Secure) not `ws://`
2. **Authentication**: Future enhancement - add JWT token in connection headers for authenticated features
3. **Rate Limiting**: Limit connections per IP address to prevent DoS attacks
4. **Input Validation**: Validate all incoming message types and payloads
5. **Origin Checking**: Verify Origin header to prevent CSRF attacks

---

## Testing Strategy

1. **Connection Tests**: Test connection establishment, handshake, disconnection
2. **Message Tests**: Test all message types (subscribe, ping, refresh_request, etc.)
3. **Reconnection Tests**: Test exponential backoff and automatic reconnection
4. **Error Handling Tests**: Test API failures, rate limiting, malformed data scenarios
5. **Load Tests**: Test 100+ concurrent WebSocket connections (SC-003)
6. **Latency Tests**: Verify <500ms perceived latency for price updates (SC-002)

---

## Summary

This WebSocket specification provides:
- Real-time price updates every 30 seconds (FR-013)
- Manual refresh capability (FR-014)
- Automatic reconnection with exponential backoff (Constitution Principle VI: Error Resilience)
- Clear error messages for user feedback (FR-019)
- Connection state transparency (FR-015: last updated timestamp)
- Fallback to cached data during API failures (FR-016, FR-022)

**Next Steps**: Create quickstart.md with setup instructions and run agent context update script.
