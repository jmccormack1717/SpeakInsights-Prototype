/** API client for backend communication */
import axios from 'axios';
import type { QueryRequest, QueryResponse, Dataset, AuthResponse, CsvUploadResult } from '../types';

// Ensure API URL ends with /api/v1
const getApiBaseUrl = () => {
  const envUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  // Remove trailing slash if present
  const baseUrl = envUrl.replace(/\/$/, '');
  // Add /api/v1 if not already present
  if (!baseUrl.endsWith('/api/v1')) {
    return `${baseUrl}/api/v1`;
  }
  return baseUrl;
};

const API_BASE_URL = getApiBaseUrl();

// Log for debugging (remove in production)
console.log('API Base URL:', API_BASE_URL);

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for debugging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.baseURL}${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', {
      url: error.config?.url,
      baseURL: error.config?.baseURL,
      fullURL: `${error.config?.baseURL}${error.config?.url}`,
      status: error.response?.status,
      message: error.message,
    });
    return Promise.reject(error);
  }
);

export const queryApi = {
  /**
   * Execute a natural language query
   */
  async executeQuery(request: QueryRequest): Promise<QueryResponse> {
    const response = await apiClient.post<QueryResponse>('/query', request);
    return response.data;
  },
};

export const authApi = {
  /**
   * Sign up a new user
   */
  async signup(email: string, password: string, fullName?: string): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/auth/signup', {
      email,
      password,
      full_name: fullName,
    });
    return response.data;
  },

  /**
   * Log in an existing user
   */
  async login(email: string, password: string): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/auth/login', {
      email,
      password,
    });
    return response.data;
  },
};

export const datasetApi = {
  /**
   * List all datasets for a user
   */
  async listDatasets(userId: string): Promise<Dataset[]> {
    const response = await apiClient.get<Dataset[]>(`/datasets/${userId}`);
    return response.data;
  },

  /**
   * Create a new dataset
   */
  async createDataset(
    userId: string,
    datasetId: string,
    name: string,
    description?: string
  ): Promise<Dataset> {
    const response = await apiClient.post<Dataset>('/datasets', {
      user_id: userId,
      dataset_id: datasetId,
      name,
      description,
    });
    return response.data;
  },

  /**
   * Delete a dataset
   */
  async deleteDataset(userId: string, datasetId: string): Promise<void> {
    await apiClient.delete(`/datasets/${userId}/${datasetId}`);
  },

  /**
   * Get schema for a dataset
   */
  async getSchema(userId: string, datasetId: string): Promise<any> {
    const response = await apiClient.get(`/datasets/${userId}/${datasetId}/schema`);
    return response.data;
  },

  /**
   * Upload CSV file to a dataset
   */
  async uploadCSV(
    userId: string,
    datasetId: string,
    file: File,
    tableName?: string
  ): Promise<CsvUploadResult> {
    const formData = new FormData();
    formData.append('file', file);
    if (tableName) {
      formData.append('table_name', tableName);
    }

    const response = await apiClient.post<CsvUploadResult>(
      `/datasets/${userId}/${datasetId}/upload`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },
};

