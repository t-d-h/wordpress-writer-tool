import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '';

const api = axios.create({
  baseURL: `${API_BASE}/api`,
  headers: { 'Content-Type': 'application/json' },
});

// AI Providers
export const getProviders = () => api.get('/ai-providers');
export const createProvider = (data) => api.post('/ai-providers', data);
export const updateProvider = (id, data) => api.put(`/ai-providers/${id}`, data);
export const deleteProvider = (id) => api.delete(`/ai-providers/${id}`);
export const verifyProvider = (data) => api.post('/ai-providers/verify', data);
export const fetchProviderModels = (data) => api.post('/ai-providers/fetch-models', data);
export const getProviderModels = (id) => api.get(`/ai-providers/${id}/models`);

// Default Models
export const getDefaultModels = () => api.get('/default-models');
export const updateDefaultModels = (data) => api.put('/default-models', data);

// WordPress Sites
export const getSites = () => api.get('/wp-sites');
export const createSite = (data) => api.post('/wp-sites', data);
export const updateSite = (id, data) => api.put(`/wp-sites/${id}`, data);
export const deleteSite = (id) => api.delete(`/wp-sites/${id}`);
export const verifySite = (data) => api.post('/wp-sites/verify', data);

// WordPress Site Posts
export const getSiteInfo = (siteId) => api.get(`/wp-sites/${siteId}/info`);
export const getSiteCategories = (siteId) => api.get(`/wp-sites/${siteId}/categories`);
export const getSitePosts = (siteId, perPage = 100, page = 1, status = null, search = null, orderby = 'date', order = 'desc', categories = null) => {
  const params = { per_page: perPage, page: page, orderby: orderby, order: order };
  if (status) params.status = status;
  if (search) params.search = search;
  if (categories) params.categories = categories;
  return api.get(`/wp-sites/${siteId}/posts`, { params });
};

// Projects
export const getProjects = () => api.get('/projects');
export const getProject = (id) => api.get(`/projects/${id}`);
export const getProjectStats = (id) => api.get(`/projects/${id}/stats`);
export const getProjectTokenUsage = (id) =>
  api.get(`/projects/${id}/stats`)
    .then(res => res.data?.token_usage || {})
    .catch(err => {
      console.error('Failed to get token usage:', err)
      return {}
    })
export const getProjectPosts = (projectId, page = 1, limit = 20, status = null, sortBy = 'date-desc', search = null) => {
  const params = { page, limit, sort_by: sortBy };
  if (status) params.status = status;
  if (search) params.search = search;
  return api.get(`/projects/${projectId}/posts`, { params });
};
export const createProject = (data) => api.post('/projects', data);
export const updateProject = (id, data) => api.put(`/projects/${id}`, data);
export const deleteProject = (id) => api.delete(`/projects/${id}`);

// Posts
export const getPostsByProject = (projectId, page = 1, limit = 100) => api.get(`/posts/by-project/${projectId}`, { params: { page, limit } });
export const getPost = (id) => api.get(`/posts/${id}`);
export const createPost = (data) => api.post('/posts', data);
export const createBulkPosts = (data) => api.post('/posts/bulk', data);
export const updatePost = (id, data) => api.put(`/posts/${id}`, data);
export const deletePost = (id) => api.delete(`/posts/${id}`);
export const publishPost = (id, forcePublish = false) =>
  api.post(`/posts/${id}/publish`, { force_publish: forcePublish });
export const unpublishPost = (id) => api.post(`/posts/${id}/unpublish`);
export const generateResearch = (id) => api.post(`/posts/${id}/generate-research`);
export const generateOutline = (id) => api.post(`/posts/${id}/generate-outline`);
export const generateContent = (id) => api.post(`/posts/${id}/generate-content`);
export const generateThumbnail = (id) => api.post(`/posts/${id}/generate-thumbnail`);
export const validateWordCount = (id) => api.post(`/posts/${id}/validate-word-count`);

export const uploadThumbnail = (id, file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post(`/posts/${id}/upload-thumbnail`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
};

export const updateThumbnailToWP = (id) =>
  api.post(`/posts/${id}/update-thumbnail-to-wp`);

export const generateThumbnailWithOptions = (id, providerId, modelName) =>
  api.post(`/posts/${id}/generate-thumbnail`, { provider_id: providerId, model_name: modelName });

// Jobs
export const getDashboardStats = () => api.get('/jobs/dashboard-stats');
export const getJob = (id) => api.get(`/jobs/${id}`);
export const getJobsByPost = (postId) => api.get(`/jobs/by-post/${postId}`);

export default api;
