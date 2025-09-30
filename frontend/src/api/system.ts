import { request } from '@/utils/request'

export const modelApi = {
  queryAll: (keyword?: string) =>
    request.get('/system/aimodel', { params: keyword ? { keyword } : {} }),
  add: (data: any) => {
    const param = data
    // 开源版本：如果 LicenseGenerator 不可用，直接使用明文
    try {
      if (typeof LicenseGenerator !== 'undefined' && LicenseGenerator.sqlbotEncrypt) {
        if (param.api_key) {
          param.api_key = LicenseGenerator.sqlbotEncrypt(data.api_key)
        }
        if (param.api_domain) {
          param.api_domain = LicenseGenerator.sqlbotEncrypt(data.api_domain)
        }
      }
    } catch (error) {
      console.warn('LicenseGenerator not available, using plain text for api_key and api_domain:', error)
    }
    return request.post('/system/aimodel', param)
  },
  edit: (data: any) => {
    const param = data
    // 开源版本：如果 LicenseGenerator 不可用，直接使用明文
    try {
      if (typeof LicenseGenerator !== 'undefined' && LicenseGenerator.sqlbotEncrypt) {
        if (param.api_key) {
          param.api_key = LicenseGenerator.sqlbotEncrypt(data.api_key)
        }
        if (param.api_domain) {
          param.api_domain = LicenseGenerator.sqlbotEncrypt(data.api_domain)
        }
      }
    } catch (error) {
      console.warn('LicenseGenerator not available, using plain text for api_key and api_domain:', error)
    }
    return request.put('/system/aimodel', param)
  },
  delete: (id: number) => request.delete(`/system/aimodel/${id}`),
  query: (id: number) => request.get(`/system/aimodel/${id}`),
  setDefault: (id: number) => request.put(`/system/aimodel/default/${id}`),
  check: (data: any) => request.fetchStream('/system/aimodel/status', data),
}
