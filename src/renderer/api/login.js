// 仅示例
import request from '@/utils/request'

export function login (data) {
  return request({
    url: '/mqtt/subscribe',
    method: 'post',
    data
  })
}

export function appInfo (params) {
  return request({
    url: '/public/app/info',
    method: 'get',
    params
  })
}