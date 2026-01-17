import { useMemo } from "react";

interface JwtUser {
  sub: string;
  role: "admin" | "user";
  exp: number;
  iat: number;
}

function decodeToken(): JwtUser | null {
  const token = localStorage.getItem("access_token");
  if (!token) return null;

  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return payload as JwtUser;
  } catch {
    return null;
  }
}

export const useAuth = () => {
  const user = useMemo(() => decodeToken(), []);

  const isAuthenticated = () => {
    if (!user) return false;
    return user.exp * 1000 > Date.now(); // token not expired
  };

  const isAdmin = () => {
    return isAuthenticated() && user?.role === "admin";
  };

  const isUser = () => {
    return isAuthenticated() && user?.role === "user";
  };

  return {
    user,
    isAuthenticated,
    isAdmin,
    isUser,
  };
};
