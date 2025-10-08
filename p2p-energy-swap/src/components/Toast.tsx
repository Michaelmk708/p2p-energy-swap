import React, { useEffect, useState } from 'react';

type ToastItem = { id: number; type: 'success' | 'error' | 'info'; message: string };

let pushToast: ((t: ToastItem) => void) | null = null;

export function showToast(message: string, type: 'success' | 'error' | 'info' = 'info') {
  if (pushToast) pushToast({ id: Date.now(), type, message });
}

export default function ToastContainer() {
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  useEffect(() => {
    pushToast = (t: ToastItem) => setToasts((s) => [...s, t]);
    return () => {
      pushToast = null;
    };
  }, []);

  useEffect(() => {
    if (!toasts.length) return;
    const timers = toasts.map((t) =>
      setTimeout(() => {
        setToasts((s) => s.filter((x) => x.id !== t.id));
      }, 4000)
    );
    return () => timers.forEach((t) => clearTimeout(t));
  }, [toasts]);

  if (!toasts.length) return null;

  return (
    <div style={{ position: 'fixed', top: 16, right: 16, zIndex: 9999 }}>
      {toasts.map((t) => (
        <div
          key={t.id}
          style={{
            marginBottom: 8,
            padding: '10px 14px',
            borderRadius: 8,
            color: '#fff',
            background: t.type === 'success' ? '#16a34a' : t.type === 'error' ? '#dc2626' : '#2563eb',
            boxShadow: '0 2px 8px rgba(0,0,0,0.12)',
            minWidth: 200
          }}
        >
          {t.message}
        </div>
      ))}
    </div>
  );
}
