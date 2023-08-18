import network from "./network";

const API_ROOT = 'http://localhost:8000';

export const serverHealthCheck = async () => {
  return await network.get(API_ROOT);
}

export const getArticles = async () => {
  return await network.get(`${API_ROOT}/articles`);
}

export const postArticles = async () => {
  return await network.post(`${API_ROOT}/articles`, {});
}
