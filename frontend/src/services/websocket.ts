/**
 * WebSocket client service for real-time price updates
 *
 * Constitution Principle V: Real-Time Updates
 * Handles WebSocket connection, reconnection, and message parsing
 */

import type { WebSocketMessage, Cryptocurrency } from '../../../shared/types/api';

// Get WebSocket URL from environment variables
const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/api/v1/ws/prices';

export type WebSocketStatus = 'connecting' | 'connected' | 'disconnected' | 'error';

export interface WebSocketClientOptions {
  onMessage?: (data: Cryptocurrency) => void;
  onStatusChange?: (status: WebSocketStatus) => void;
  onError?: (error: Error) => void;
  autoReconnect?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

/**
 * WebSocket client for real-time cryptocurrency price updates
 *
 * Features:
 * - Automatic reconnection with exponential backoff
 * - Connection status tracking
 * - Message parsing and validation
 * - Error handling
 */
export class WebSocketClient {
  private ws: WebSocket | null = null;
  private status: WebSocketStatus = 'disconnected';
  private reconnectAttempts = 0;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private options: Required<WebSocketClientOptions>;

  constructor(options: WebSocketClientOptions = {}) {
    this.options = {
      onMessage: options.onMessage || (() => {}),
      onStatusChange: options.onStatusChange || (() => {}),
      onError: options.onError || (() => {}),
      autoReconnect: options.autoReconnect ?? true,
      reconnectInterval: options.reconnectInterval ?? 1000, // Start with 1 second
      maxReconnectAttempts: options.maxReconnectAttempts ?? 10,
    };
  }

  /**
   * Connect to WebSocket server
   */
  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      return; // Already connected
    }

    this.updateStatus('connecting');

    try {
      this.ws = new WebSocket(WS_URL);

      this.ws.onopen = () => this.handleOpen();
      this.ws.onmessage = (event) => this.handleMessage(event);
      this.ws.onerror = (event) => this.handleError(event);
      this.ws.onclose = () => this.handleClose();
    } catch (error) {
      this.handleError(error as Event);
    }
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect(): void {
    this.clearReconnectTimer();
    this.options.autoReconnect = false; // Disable auto-reconnect

    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }

    this.updateStatus('disconnected');
  }

  /**
   * Get current connection status
   */
  getStatus(): WebSocketStatus {
    return this.status;
  }

  /**
   * Handle WebSocket open event
   */
  private handleOpen(): void {
    console.log('✅ WebSocket connected');
    this.reconnectAttempts = 0;
    this.clearReconnectTimer();
    this.updateStatus('connected');
  }

  /**
   * Handle WebSocket message event
   */
  private handleMessage(event: MessageEvent): void {
    try {
      const message: WebSocketMessage = JSON.parse(event.data);

      switch (message.type) {
        case 'connected':
          console.log('🔌 WebSocket connection acknowledged');
          break;

        case 'price_update':
          // Parse timestamps from ISO strings to Date objects
          const crypto = this.parseCryptocurrency(message.data);
          this.options.onMessage(crypto);
          break;

        case 'error':
          console.error('❌ WebSocket error from server:', message.message);
          this.options.onError(new Error(message.message));
          break;

        default:
          console.warn('⚠️  Unknown WebSocket message type:', message);
      }
    } catch (error) {
      console.error('❌ Failed to parse WebSocket message:', error);
      this.options.onError(
        new Error(`Failed to parse message: ${error instanceof Error ? error.message : 'Unknown'}`)
      );
    }
  }

  /**
   * Handle WebSocket error event
   */
  private handleError(event: Event): void {
    console.error('❌ WebSocket error:', event);
    this.updateStatus('error');
    this.options.onError(new Error('WebSocket connection error'));
  }

  /**
   * Handle WebSocket close event
   */
  private handleClose(): void {
    console.log('👋 WebSocket disconnected');
    this.updateStatus('disconnected');

    // Attempt reconnection if enabled
    if (this.options.autoReconnect && this.reconnectAttempts < this.options.maxReconnectAttempts) {
      this.scheduleReconnect();
    } else if (this.reconnectAttempts >= this.options.maxReconnectAttempts) {
      console.error('❌ Max reconnect attempts reached');
      this.options.onError(new Error('Failed to reconnect after maximum attempts'));
    }
  }

  /**
   * Schedule reconnection with exponential backoff
   */
  private scheduleReconnect(): void {
    this.clearReconnectTimer();

    // Exponential backoff: 1s, 2s, 4s, 8s, max 30s
    const delay = Math.min(
      this.options.reconnectInterval * Math.pow(2, this.reconnectAttempts),
      30000
    );

    console.log(`🔄 Reconnecting in ${delay / 1000}s (attempt ${this.reconnectAttempts + 1}/${this.options.maxReconnectAttempts})`);

    this.reconnectTimer = setTimeout(() => {
      this.reconnectAttempts++;
      this.connect();
    }, delay);
  }

  /**
   * Clear reconnect timer
   */
  private clearReconnectTimer(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }

  /**
   * Update connection status and notify listeners
   */
  private updateStatus(status: WebSocketStatus): void {
    this.status = status;
    this.options.onStatusChange(status);
  }

  /**
   * Parse cryptocurrency data from WebSocket message
   * Converts ISO timestamp strings to Date objects
   */
  private parseCryptocurrency(data: any): Cryptocurrency {
    return {
      ...data,
      lastUpdated: new Date(data.lastUpdated),
      sparklineData: data.sparklineData?.map((point: any) => ({
        ...point,
        timestamp: new Date(point.timestamp),
      })) || [],
    };
  }
}
