"use client";

import {
  createContext,
  useContext,
  useMemo,
  useSyncExternalStore,
} from "react";
import { STORAGE_KEYS, clearSession } from "../lib/api";
import type { AuthUser, UserProfile } from "../lib/types";

type UserContextType = {
  profile: UserProfile | null;
  authUser: AuthUser | null;
  token: string | null;
  isAuthenticated: boolean;
  setProfile: (p: UserProfile) => void;
  setAuthSession: (tokenValue: string, user: AuthUser) => void;
  clearProfile: () => void;
  logout: () => void;
};

const UserContext = createContext<UserContextType | null>(null);
const STORAGE_EVENT = "app-storage-change";

function emitStorageChange() {
  if (typeof window === "undefined") {
    return;
  }

  window.dispatchEvent(new Event(STORAGE_EVENT));
}

function subscribeToStorage(callback: () => void) {
  if (typeof window === "undefined") {
    return () => undefined;
  }

  const handler = () => callback();

  window.addEventListener("storage", handler);
  window.addEventListener(STORAGE_EVENT, handler);

  return () => {
    window.removeEventListener("storage", handler);
    window.removeEventListener(STORAGE_EVENT, handler);
  };
}

function parseStoredJson<T>(rawValue: string | null): T | null {
  if (!rawValue) {
    return null;
  }

  try {
    return JSON.parse(rawValue) as T;
  } catch {
    return null;
  }
}

function readStoredJsonText(key: string): string | null {
  if (typeof window === "undefined") {
    return null;
  }

  return window.localStorage.getItem(key);
}

function readStoredText(key: string): string | null {
  if (typeof window === "undefined") {
    return null;
  }

  return window.localStorage.getItem(key);
}

export function UserProvider({ children }: { children: React.ReactNode }) {
  const profileSnapshot = useSyncExternalStore(
    subscribeToStorage,
    () => readStoredJsonText(STORAGE_KEYS.profile),
    () => null,
  );
  const authUserSnapshot = useSyncExternalStore(
    subscribeToStorage,
    () => readStoredJsonText(STORAGE_KEYS.authUser),
    () => null,
  );
  const token = useSyncExternalStore(
    subscribeToStorage,
    () => readStoredText(STORAGE_KEYS.token),
    () => null,
  );
  const profile = useMemo(
    () => parseStoredJson<UserProfile>(profileSnapshot),
    [profileSnapshot],
  );
  const authUser = useMemo(
    () => parseStoredJson<AuthUser>(authUserSnapshot),
    [authUserSnapshot],
  );

  const setProfile = (nextProfile: UserProfile) => {
    window.localStorage.setItem(
      STORAGE_KEYS.profile,
      JSON.stringify(nextProfile),
    );
    emitStorageChange();
  };

  const setAuthSession = (tokenValue: string, user: AuthUser) => {
    window.localStorage.setItem(STORAGE_KEYS.token, tokenValue);
    window.localStorage.setItem(STORAGE_KEYS.authUser, JSON.stringify(user));
    emitStorageChange();
  };

  const clearProfile = () => {
    window.localStorage.removeItem(STORAGE_KEYS.profile);
    emitStorageChange();
  };

  const logout = () => {
    clearSession();
    emitStorageChange();
  };

  return (
    <UserContext.Provider
      value={{
        profile,
        authUser,
        token,
        isAuthenticated: Boolean(token),
        setProfile,
        setAuthSession,
        clearProfile,
        logout,
      }}
    >
      {children}
    </UserContext.Provider>
  );
}

export const useUser = () => {
  const ctx = useContext(UserContext);
  if (!ctx) throw new Error("useUser must be used inside UserProvider");
  return ctx;
};
