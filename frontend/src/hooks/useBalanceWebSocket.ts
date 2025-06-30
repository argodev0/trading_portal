import { useEffect, useRef, useState } from 'react';

export interface BalanceUpdate {
  type: string;
  data: any[];
  timestamp: string;
}

export function useBalanceWebSocket(authToken: string) {
  const [balances, setBalances] = useState<any[]>([]);
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!authToken) return;
    
    const wsProtocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const wsUrl = `${wsProtocol}://${window.location.host}/ws/balances/?token=${authToken}`;
    
    console.log('Connecting to WebSocket:', wsUrl);
    
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('WebSocket connected');
      setConnected(true);
      setError(null);
    };
    
    ws.onclose = (event) => {
      console.log('WebSocket disconnected:', event.code, event.reason);
      setConnected(false);
    };
    
    ws.onerror = (event) => {
      console.error('WebSocket error:', event);
      setConnected(false);
      setError('WebSocket connection failed');
    };
    
    ws.onmessage = (event) => {
      try {
        const msg: BalanceUpdate = JSON.parse(event.data);
        console.log('WebSocket message received:', msg);
        if (msg.type === 'balance_update') {
          setBalances(msg.data);
        }
      } catch (e) {
        console.error('Failed to parse WebSocket message:', e);
      }
    };
    
    return () => {
      console.log('Cleaning up WebSocket connection');
      ws.close();
    };
  }, [authToken]);

  const refreshBalances = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action: 'refresh_balances' }));
    }
  };

  return { balances, connected, error, refreshBalances };
}
