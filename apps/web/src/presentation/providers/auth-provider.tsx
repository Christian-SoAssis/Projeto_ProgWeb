"use client"

import React, { createContext, useContext, useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { UserEntity } from "../../domain/entities/user.entity";

import { LoginDto } from "../../application/dto/login.dto";
import { RegisterClientDto } from "../../application/dto/register-client.dto";
import { RegisterProfessionalDto } from "../../application/dto/register-professional.dto";
import {
  loginUseCase,
  registerClientUseCase,
  registerProfessionalUseCase,
  logoutUseCase,
  getCurrentUserUseCase,
  switchRoleUseCase,
  oauthLoginUseCase,
} from "../container";

interface AuthContextType {
  user: UserEntity | null;
  loading: boolean;
  isAuthenticated: boolean;
  login: (credentials: LoginDto) => Promise<void>;
  oauthLogin: (accessToken: string, refreshToken: string) => Promise<void>;
  registerClient: (data: RegisterClientDto) => Promise<void>;
  registerPro: (dto: RegisterProfessionalDto) => Promise<{ requiresManualLogin: boolean }>;
  switchRole: () => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserEntity | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  const logout = useCallback(() => {
    logoutUseCase.execute();
    setUser(null);
    router.push("/login");
  }, [router]);

  useEffect(() => {
    async function loadUser() {
      try {
        const currentUser = await getCurrentUserUseCase.execute();
        setUser(currentUser);
      } catch (error) {
        console.error("Falha ao carregar usuário inicial:", error);
        logout();
      } finally {
        setLoading(false);
      }
    }
    loadUser();
  }, [logout]);

  const login = async (credentials: LoginDto) => {
    const loggedUser = await loginUseCase.execute(credentials);
    setUser(loggedUser);

    if (loggedUser.role === "professional") {
      router.push("/dashboard/pro");
    } else {
      router.push("/dashboard/client");
    }
  };

  const registerClient = async (data: RegisterClientDto) => {
    const loggedUser = await registerClientUseCase.execute(data);
    setUser(loggedUser);
    router.push("/dashboard/client");
  };

  const registerPro = async (dto: RegisterProfessionalDto) => {
    const result = await registerProfessionalUseCase.execute(dto);

    if ("requiresManualLogin" in result) {
      router.push("/login?registered=true");
      return { requiresManualLogin: true };
    } else {
      setUser(result.user);
      router.push("/dashboard/pro");
      return { requiresManualLogin: false };
    }
  };

  const oauthLogin = async (accessToken: string, refreshToken: string) => {
    const loggedUser = await oauthLoginUseCase.execute(accessToken, refreshToken);
    setUser(loggedUser);

    if (loggedUser.role === "professional") {
      router.push("/dashboard/pro");
    } else {
      router.push("/dashboard/client");
    }
  };

  const switchRole = async () => {
    try {
      const loggedUser = await switchRoleUseCase.execute();
      setUser(loggedUser);

      if (loggedUser.role === "professional") {
        router.push("/dashboard/pro");
      } else {
        router.push("/dashboard/client");
      }
    } catch (error) {
      console.error("Falha ao alternar perfil de acesso:", error);
      throw error;
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        isAuthenticated: !!user,
        login,
        oauthLogin,
        registerClient,
        registerPro,
        switchRole,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth deve ser usado dentro de um AuthProvider");
  }
  return context;
};
