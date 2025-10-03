import { createContext, useContext, useState, ReactNode } from "react";

export interface Notification {
  id: string;
  type: "buy" | "sell";
  message: string;
  timestamp: Date;
  read: boolean;
}

interface NotificationContextType {
  notifications: Notification[];
  addNotification: (notification: Omit<Notification, "id" | "timestamp" | "read">) => void;
  markAsRead: (id: string) => void;
  markAllAsRead: () => void;
  unreadCount: number;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export function NotificationProvider({ children }: { children: ReactNode }) {
  const [notifications, setNotifications] = useState<Notification[]>([
    {
      id: "1",
      type: "buy",
      message: "SolarFarm_42 bought 50 tokens from you for KES 600",
      timestamp: new Date(Date.now() - 3600000),
      read: false,
    },
    {
      id: "2",
      type: "sell",
      message: "You successfully sold 25 tokens to GreenHome_89",
      timestamp: new Date(Date.now() - 7200000),
      read: false,
    },
    {
      id: "3",
      type: "buy",
      message: "EcoVilla_23 bought 30 tokens from you for KES 375",
      timestamp: new Date(Date.now() - 10800000),
      read: false,
    },
  ]);

  const addNotification = (notification: Omit<Notification, "id" | "timestamp" | "read">) => {
    const newNotification: Notification = {
      ...notification,
      id: Date.now().toString(),
      timestamp: new Date(),
      read: false,
    };
    setNotifications((prev) => [newNotification, ...prev]);
  };

  const markAsRead = (id: string) => {
    setNotifications((prev) =>
      prev.map((notif) => (notif.id === id ? { ...notif, read: true } : notif))
    );
  };

  const markAllAsRead = () => {
    setNotifications((prev) => prev.map((notif) => ({ ...notif, read: true })));
  };

  const unreadCount = notifications.filter((n) => !n.read).length;

  return (
    <NotificationContext.Provider
      value={{ notifications, addNotification, markAsRead, markAllAsRead, unreadCount }}
    >
      {children}
    </NotificationContext.Provider>
  );
}

export function useNotifications() {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error("useNotifications must be used within NotificationProvider");
  }
  return context;
}
