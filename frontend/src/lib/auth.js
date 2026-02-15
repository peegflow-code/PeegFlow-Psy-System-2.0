const KEY = "token";

export function getToken() {
  return localStorage.getItem(KEY);
}

export function saveToken(token) {
  localStorage.setItem(KEY, token);
  return token;
}

export function clearToken() {
  localStorage.removeItem(KEY);
}