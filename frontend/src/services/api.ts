import axios from 'axios';
import { Symptom, UserProfile, Consultation, SyncQueueItem } from '../store/healthStore';

// In Cloud Run deployment, frontend and backend share same domain
const API_BASE = process.env.EXPO_PUBLIC_BACKEND_URL || '';

const api = axios.create({
  baseURL: API_BASE ? `${API_BASE}/api` : '/api',  // Relative URL when deployed together
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface TriageRequest {
  user_id: string;
  symptoms: { id: string; name_en: string; name_bn: string }[];
  duration?: string;
}

export interface TriageResponse {
  id: string;
  severity_level: string;
  ai_explanation: string;
  guidance_bangla: string;
  guidance_english: string;
  is_offline_result: boolean;
  created_at: string;
}

export const healthAPI = {
  // Health check
  healthCheck: async () => {
    const response = await api.get('/health');
    return response.data;
  },

  // Symptoms
  getSymptoms: async (): Promise<Symptom[]> => {
    const response = await api.get('/symptoms');
    return response.data.symptoms;
  },

  // Users
  createUser: async (user: { age: number; gender: string; location?: string }): Promise<UserProfile> => {
    const response = await api.post('/users', user);
    return response.data;
  },

  getUser: async (userId: string): Promise<UserProfile> => {
    const response = await api.get(`/users/${userId}`);
    return response.data;
  },

  updateUser: async (userId: string, user: { age: number; gender: string; location?: string }): Promise<UserProfile> => {
    const response = await api.put(`/users/${userId}`, user);
    return response.data;
  },

  // Triage
  performTriage: async (request: TriageRequest): Promise<TriageResponse> => {
    const response = await api.post('/triage', request);
    return response.data;
  },

  // Offline Triage (rule-based)
  performOfflineTriage: async (request: TriageRequest): Promise<TriageResponse> => {
    const response = await api.post('/triage/offline', request);
    return response.data;
  },

  // Consultations
  getConsultations: async (userId: string): Promise<Consultation[]> => {
    const response = await api.get(`/consultations/${userId}`);
    return response.data;
  },

  // Sync
  syncOfflineData: async (items: { action: string; payload: any }[]) => {
    const response = await api.post('/sync', { items });
    return response.data;
  },
};

export default api;
