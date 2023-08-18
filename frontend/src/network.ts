import axios from 'axios';

axios.defaults.withCredentials = false;
axios.defaults.headers.post['Access-Control-Allow-Origin'] = '*';
axios.defaults.headers.post['Access-Control-Allow-Credentials'] = 'true';

export const headers = {
  'Content-Type': 'application/json',
  'Cache-Control': 'no-cache',
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Credentials': 'true',
};

const get = (endpoint: string, params?: Record<string, unknown>) =>
  axios.get(`${endpoint}`, params);

const post = (
  endpoint: string,
  body: Record<string, unknown>,
  params?: Record<string, unknown>,
) => axios.post(`${endpoint}`, body, params);

const patch = (
  endpoint: string,
  body: Record<string, unknown> | Record<string, unknown>[],
  params?: Record<string, unknown>,
) => axios.patch(`${endpoint}`, body, params);

const put = (
  endpoint: string,
  body: Record<string, unknown> | Record<string, unknown>[],
  params?: Record<string, unknown>,
) => axios.put(`${endpoint}`, body, params);

const del = (endpoint: string, params?: Record<string, unknown>) =>
  axios.delete(`${endpoint}`, params);

const network = {
  get,
  post,
  patch,
  put,
  del,
};

export default network;
