import { request } from '@/utils/request'
export const AuthApi = {
  login: (credentials: { username: string; password: string }) => {
    // 开源版本：如果 LicenseGenerator 不可用，直接使用明文
    let entryCredentials
    try {
      if (typeof LicenseGenerator !== 'undefined' && LicenseGenerator.sqlbotEncrypt) {
        entryCredentials = {
          username: LicenseGenerator.sqlbotEncrypt(credentials.username),
          password: LicenseGenerator.sqlbotEncrypt(credentials.password),
        }
      } else {
        entryCredentials = credentials
      }
    } catch (error) {
      console.warn('LicenseGenerator not available, using plain credentials:', error)
      entryCredentials = credentials
    }
    return request.post<{
      data: any
      token: string
    }>('/login/access-token', entryCredentials, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })
  },
  logout: () => request.post('/auth/logout'),
  info: () => request.get('/user/info'),
}
