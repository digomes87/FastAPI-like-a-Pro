export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface TokenData {
  sub: string;
  exp: number;
}

export interface AuthState {
  isAuthenticated: boolean;
  token: string | null;
  user: any | null;
}

export interface GoogleAuthResponse {
  access_token: string;
  token_type: string;
  user: any;
}
