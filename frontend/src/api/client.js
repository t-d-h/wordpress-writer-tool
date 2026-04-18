import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '';

const apiClient = axios.create({
  baseURL: `${API_BASE}/api`,
  headers: { 'Content-Type': 'application/json' },
});

// Add request interceptor to inject token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Add response interceptor to handle 401 errors
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      // Token expired or invalid, redirect to login
      localStorage.removeItem('auth_token')
      localStorage.removeItem('auth_user')
      window.location.href = '/login'
      return Promise.reject(error)
    }

    return Promise.reject(error)
  }
)

// AI Providers
export const getProviders = () => apiClient.get('/ai-providers');
export const createProvider = (data) => apiClient.post('/ai-providers', data);
export const updateProvider = (id, data) => apiClient.put(`/ai-providers/${id}`, data);
export const deleteProvider = (id) => apiClient.delete(`/ai-providers/${id}`);
export const verifyProvider = (data) => apiClient.post('/ai-providers/verify', data);
export const fetchProviderModels = (data) => apiClient.post('/ai-providers/fetch-models', data);
export const getProviderModels = (id) => apiClient.get(`/ai-providers/${id}/models`);

// Default Models
export const getDefaultModels = () => apiClient.get('/default-models');
export const updateDefaultModels = (data) => apiClient.put('/default-models', data);

// WordPress Sites
export const getSites = () => apiClient.get('/wp-sites');
export const createSite = (data) => apiClient.post('/wp-sites', data);
export const updateSite = (id, data) => apiClient.put(`/wp-sites/${id}`, data);
export const deleteSite = (id) => apiClient.delete(`/wp-sites/${id}`);
export const verifySite = (data) => apiClient.post('/wp-sites/verify', data);

// WordPress Site Posts
export const getSiteInfo = (siteId) => apiClient.get(`/wp-sites/${siteId}/info`);
export const getSiteCategories = (siteId) => apiClient.get(`/wp-sites/${siteId}/categories`);
export const getSitePosts = (siteId, perPage = 100, page = 1, status = null, search = null, orderby = 'date', order = 'desc', categories = null) => {
  const params = { per_page: perPage, page: page, orderby: orderby, order: order };
  if (status) params.status = status;
  if (search) params.search = search;
  if (categories) params.categories = categories;
  return apiClient.get(`/wp-sites/${siteId}/posts`, { params });
};

// Projects
export const getProjects = () => apiClient.get('/projects');
export const getProject = (id) => apiClient.get(`/projects/${id}`);
export const getProjectStats = (id) => apiClient.get(`/projects/${id}/stats`);
export const getProjectTokenUsage = (id) =>
  apiClient.get(`/projects/${id}/stats`)
    .then(res => res.data?.token_usage || {})
    .catch(err => {
      console.error('Failed to get token usage:', err)
      return {}
    })
export const getProjectPosts = (projectId, page = 1, limit = 20, status = null, sortBy = 'date-desc', search = null) => {
  const params = { page, limit, sort_by: sortBy };
  if (status) params.status = status;
  if (search) params.search = search;
  return apiClient.get(`/projects/${projectId}/posts`, { params });
};
export const createProject = (data) => apiClient.post('/projects', data);
export const updateProject = (id, data) => apiClient.put(`/projects/${id}`, data);
export const deleteProject = (id) => apiClient.delete(`/projects/${id}`);

// Posts
export const getPostsByProject = (projectId, page = 1, limit = 100) => apiClient.get(`/posts/by-project/${projectId}`, { params: { page, limit } });
export const getPost = (id) => apiClient.get(`/posts/${id}`);
export const createPost = (data) => apiClient.post('/posts', data);
export const createBulkPosts = (data) => apiClient.post('/posts/bulk', data);
export const updatePost = (id, data) => apiClient.put(`/posts/${id}`, data);
export const deletePost = (id) => apiClient.delete(`/posts/${id}`);
export const publishPost = (id, forcePublish = false) =>
  apiClient.post(`/posts/${id}/publish`, { force_publish: forcePublish });
export const unpublishPost = (id) => apiClient.post(`/posts/${id}/unpublish`);
export const generateResearch = (id) => apiClient.post(`/posts/${id}/generate-research`);
export const generateOutline = (id) => apiClient.post(`/posts/${id}/generate-outline`);
export const generateContent = (id) => apiClient.post(`/posts/${id}/generate-content`);
export const generateThumbnail = (id) => apiClient.post(`/posts/${id}/generate-thumbnail`);
export const validateWordCount = (id) => apiClient.post(`/posts/${id}/validate-word-count`);

export const uploadThumbnail = (id, file) => {
  const formData = new FormData();
  formData.append('file', file);
  return apiClient.post(`/posts/${id}/upload-thumbnail`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
};

export const updateThumbnailToWP = (id) =>
  apiClient.post(`/posts/${id}/update-thumbnail-to-wp`);

export const generateThumbnailWithOptions = (id, providerId, modelName) =>
  apiClient.post(`/posts/${id}/generate-thumbnail`, { provider_id: provider_id, model_name: modelName });

// Jobs
export const getDashboardStats = () => apiClient.get('/jobs/dashboard-stats');
export const getJob = (id) => apiClient.get(`/jobs/${id}`);
export const getJobsByPost = (postId) => apiClient.get(`/jobs/by-post/${postId}`);

// Link Map
export const getLinkMap = (projectId) => apiClient.get(`/projects/${projectId}/link-map`);
export const refreshLinkMap = (projectId) => apiClient.post(`/projects/${projectId}/link-map/refresh`);

// Authentication
export const login = async (username, password) => {
  const params = new URLSearchParams()
  params.append('username', username)
  params.append('password', password)

  return apiClient.post('/auth/login', params, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  })
}

export default apiClient;
