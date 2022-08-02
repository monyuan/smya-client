// 仅示例
import request from '@/utils/request'

export function login (data) {
  return request({
    url: '/device/login',
    method: 'post',
    data
  })
}

