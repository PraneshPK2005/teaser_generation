import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Generate teaser from YouTube URL
export const generateTeaserFromYouTube = async (youtubeUrl, method, maxLength, minLength) => {
  const formData = new FormData();
  formData.append('youtube_url', youtubeUrl);
  formData.append('method', method);
  formData.append('max_length', maxLength);
  formData.append('min_length', minLength);
  
  try {
    const response = await api.post('/api/generate-teaser', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to generate teaser');
  }
};

// Generate teaser from uploaded file
export const generateTeaserFromFile = async (file, method, maxLength, minLength) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('method', method);
  formData.append('max_length', maxLength);
  formData.append('min_length', minLength);
  
  try {
    const response = await api.post('/api/generate-teaser', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to generate teaser');
  }
};

export const getTaskStatus = async (taskId) => {
  try {
    const response = await api.get(`/api/task-status/${taskId}`);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to get task status');
  }
};

export const downloadTeaser = async (taskId) => {
  try {
    const response = await api.get(`/api/download-teaser/${taskId}`, {
      responseType: 'blob',
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to download teaser');
  }
};

export const listTasks = async () => {
  try {
    const response = await api.get('/api/tasks');
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to list tasks');
  }
};

export const deleteTask = async (taskId) => {
  try {
    const response = await api.delete(`/api/task/${taskId}`);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to delete task');
  }
};