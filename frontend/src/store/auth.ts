import { create } from "zustand";

interface AuthState {
  token: string | null;
  userId: string | null;
  profile: UserProfile | null;
  isAuthenticated: boolean;
  setAuth: (token: string, userId: string) => void;
  setProfile: (profile: UserProfile) => void;
  logout: () => void;
}

export interface UserProfile {
  id: string;
  email: string;
  name: string;
  reading_level: string;
  preset: "Dislexia" | "TDAH" | "Combinado" | "Docente";
  tone: string;
  avoid_words: string[];
  max_sentence_length: number;
  fatigue_history?: { date: string; level: string; preset: string }[];
}

export const useAuthStore = create<AuthState>((set) => ({
  token: localStorage.getItem("token"),
  userId: localStorage.getItem("userId"),
  profile: null,
  isAuthenticated: !!localStorage.getItem("token"),

  setAuth: (token, userId) => {
    localStorage.setItem("token", token);
    localStorage.setItem("userId", userId);
    set({ token, userId, isAuthenticated: true });
  },

  setProfile: (profile) => set({ profile }),

  logout: () => {
    localStorage.removeItem("token");
    localStorage.removeItem("userId");
    set({ token: null, userId: null, profile: null, isAuthenticated: false });
  },
}));
