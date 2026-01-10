/**
 * useWebSocket custom hook
 *
 * React hook for managing WebSocket connections with reconnection logic
 * Constitution Principle V: Real-Time Updates
 */

import { useEffect, useRef, useState } from 'react';
import { WebSocketClient, WebSocketStatus } from '../services/websocket';
import type { Cryptocurrency } from '../../../shared/types/api';

export interface UseWebSocketOptions {
  autoConnect?: boolean;
  autoReconnect?: boolean;
  onMessage?: (data: Cryptocurrency) => void;
  onError?: (error: Error) => void;
}

export interface UseWebSocketReturn {
  status: WebSocketStatus;
  connect: () => void;
  disconnect: () => void;
  lastMessage: Cryptocurrency | null;
  error: Error | null;
}

/**
 * Custom hook for WebSocket connection management
 *
 * Features:
 * - Automatic connection on mount (optional)
 * - Automatic reconnection with exponential backoff
 * - Connection status tracking
 * - Message handling
 * - Cleanup on unmount
 *
 * @param options - WebSocket configuration options
 * @returns WebSocket state and control functions
 */
export function useWebSocket(options: UseWebSocketOptions = {}): UseWebSocketReturn {
  const {
    autoConnect = true,
    autoReconnect = true,
    onMessage,
    onError,
  } = options;

  const [status, setStatus] = useState<WebSocketStatus>('disconnected');
  const [lastMessage, setLastMessage] = useState<Cryptocurrency | null>(null);
  const [error, setError] = useState<Error | null>(null);

  const clientRef = useRef<WebSocketClient | null>(null);

  // Initialize WebSocket client
  useEffect(() => {
    clientRef.current = new WebSocketClient({
      autoReconnect,
      onMessage: (data) => {
        setLastMessage(data);
        setError(null);
        onMessage?.(data);
      },
      onStatusChange: (newStatus) => {
        setStatus(newStatus);
      },
      onError: (err) => {
        setError(err);
        onError?.(err);
      },
    });

    // Auto-connect if enabled
    if (autoConnect) {
      clientRef.current.connect();
    }

    // Cleanup on unmount
    return () => {
      clientRef.current?.disconnect();
    };
  }, []); // Empty deps - only run once on mount

  const connect = () => {
    clientRef.current?.connect();
  };

  const disconnect = () => {
    clientRef.current?.disconnect();
  };

  return {
    status,
    connect,
    disconnect,
    lastMessage,
    error,
  };
}
