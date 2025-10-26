"use client";
import React, { createContext, useContext, useState, useEffect } from "react";

interface User {
  email: string;
  full_name?: string;
  given_name?: string;
  family_name?: string;
  picture?: string;
  locale?: string;
  verified_email?: boolean;
}

interface SessionContextProps {
  user: User | null;
  loading: boolean;
  refreshSession: () => Promise<void>;
}

const SessionContext = createContext<SessionContextProps>({
  user: null,
  loading: true,
  refreshSession: async () => {},
});

export const SessionProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchSession = async () => {
    setLoading(true);
    try {
      const res = await fetch("https://mindblocks-backend.onrender.com/me", {
        credentials: "include",
      });
      if (res.ok) {
        const data = await res.json();
        setUser(data.user);
      } else {
        setUser(null);
      }
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSession();
  }, []);

  return (
    <SessionContext.Provider value={{ user, loading, refreshSession: fetchSession }}>
      {children}
    </SessionContext.Provider>
  );
};

export const useSession = () => useContext(SessionContext)
