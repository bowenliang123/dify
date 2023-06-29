import { get, post } from './base'

export const getList = (params: { page: number; limit: number }) => {
  return get('/account/list', {
    params,
  })
}

export const addUsers = (params: { name: string; email: string; password: string }) => {
  return post('/account/add', {
    body: params,
  })
}
