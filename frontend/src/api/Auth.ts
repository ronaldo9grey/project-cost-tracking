import request from './axios'

export interface LoginParams {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
}

export interface UserInfo {
  id: number
  username: string
  role_id: number
  role?: {
    id: number
    name: string
    description: string
  }
}

export const login = (params: LoginParams) => {
  // 使用表单数据格式发送登录请求
  const formData = new URLSearchParams()
  formData.append('username', params.username)
  formData.append('password', params.password)
  console.log('发送登录请求:', params.username)
  return request.post('/api/v1/auth/login', formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  })
}

export const getUserInfo = () => {
  return request.get<UserInfo>('/api/v1/auth/users/me')
}

export const logout = () => {
  return request.post('/api/v1/auth/logout')
}

export const refreshToken = () => {
  return request.post<LoginResponse>('/api/v1/auth/refresh')
}

export interface ChangePasswordParams {
  old_password: string
  new_password: string
  confirm_password: string
}

export const changePassword = (params: ChangePasswordParams) => {
  return request.post('/api/v1/auth/change-password', params)
}

// Token管理
export const getToken = () => {
  return localStorage.getItem('token')
}

export const setToken = (token: string) => {
  localStorage.setItem('token', token)
}

export const removeToken = () => {
  localStorage.removeItem('token')
}

export const getTokenExpireTime = () => {
  return localStorage.getItem('token_expire_time')
}

export const setTokenExpireTime = (time: string) => {
  localStorage.setItem('token_expire_time', time)
}
