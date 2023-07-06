import { get, post } from './base'

export const getAll = (params: { page: number; limit: number }) => {
  return get('/workspaces/all', {
    params,
  })
}

export const addWorkspace = (params: { name: string }) => {
  return post('/workspaces/add', {
    body: params,
  })
}

export const getUsers = (params: { tenant_id: string }) => {
  return get('/workspaces/users', {
    params,
  })
}

export const getListbyname = (params: { name: string }) => {
  return get('/account/listbyname', {
    params,
  })
}

export const connectUsers = (params: { tenant_id: string; user_id: string }) => {
  return post('/workspaces/users', {
    body: params,
  })
}
