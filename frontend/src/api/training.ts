import { request } from '@/utils/request'

export const trainingApi = {
  getList: (pageNum: any, pageSize: any, params: any) =>
    request.get(`/system/data-training/page/${pageNum}/${pageSize}`, {
      params,
    }),
  updateEmbedded: (data: any) => request.put('/system/data-training', data),
  deleteEmbedded: (params: any) => request.delete('/system/data-training', { data: params }),
  getOne: (id: any) => request.get(`/system/data-training/${id}`),
}
