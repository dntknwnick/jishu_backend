// API Service Layer for Jishu Backend Integration
const API_BASE_URL = 'http://localhost:5000';

// Types for API responses
export interface ApiResponse<T = any> {
  success: boolean;
  message: string;
  data?: T;
  error?: string;
}

export interface User {
  id: number;
  email_id: string;
  name: string;
  mobile_no?: string;
  is_premium: boolean;
  is_admin: boolean;
  color_theme: string;
  status: string;
  created_at: string;
  source?: string;
  auth_provider?: string;
}

export interface Course {
  id: number;
  course_name: string;
  description: string;
  created_at: string;
  subjects?: Subject[];
}

export interface Subject {
  id: number;
  subject_name: string;
  exam_category_id: number;
  amount?: number;
  offer_amount?: number;
  max_tokens?: number;
  total_mock?: number;
  is_deleted?: boolean;
  is_bundle?: boolean;
  created_at: string;
}

export interface BlogPost {
  id: number;
  title: string;
  content: string;
  tags: string[];
  user_id: number;
  user?: {
    id: number;
    name: string;
    email_id: string;
  };
  created_at: string;
  updated_at: string;
  likes_count: number;
  comments_count: number;
  is_liked?: boolean;
  is_featured?: boolean;
  status?: string;
  // Computed fields for UI
  author?: {
    name: string;
    avatar?: string;
    role?: string;
  };
  timeAgo?: string;
  likes?: number;
  comments?: number;
  views?: number;
}

export interface Question {
  id: number;
  question_text: string;
  option_a: string;
  option_b: string;
  option_c: string;
  option_d: string;
  correct_answer: string;
  subject_id: number;
  difficulty_level: string;
  created_at: string;
}

// API Error class
export class ApiError extends Error {
  constructor(public status: number, message: string, public data?: any) {
    super(message);
    this.name = 'ApiError';
  }
}

// Get auth token from localStorage
const getAuthToken = (): string | null => {
  return localStorage.getItem('access_token');
};

// Get refresh token from localStorage
const getRefreshToken = (): string | null => {
  return localStorage.getItem('refresh_token');
};

// Save both access and refresh tokens
export const saveTokens = (accessToken: string, refreshToken: string): void => {
  localStorage.setItem('access_token', accessToken);
  localStorage.setItem('refresh_token', refreshToken);
};

// Refresh access token using refresh token
const refreshAccessToken = async (): Promise<string | null> => {
  const refreshToken = getRefreshToken();
  if (!refreshToken) return null;

  try {
    const response = await fetch(`${API_BASE_URL}/refresh-token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${refreshToken}`
      }
    });

    if (response.ok) {
      const data = await response.json();
      if (data.success && data.data?.access_token) {
        localStorage.setItem('access_token', data.data.access_token);
        // Also store the new refresh token if provided
        if (data.data?.refresh_token) {
          localStorage.setItem('refresh_token', data.data.refresh_token);
        }
        return data.data.access_token;
      }
    }
  } catch (error) {
    console.error('Failed to refresh token:', error);
  }

  return null;
};

// Generic API request function
export const apiRequest = async <T = any>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> => {
  const url = `${API_BASE_URL}${endpoint}`;
  const token = getAuthToken();

  const defaultHeaders: HeadersInit = {
    'Content-Type': 'application/json',
  };

  if (token) {
    defaultHeaders.Authorization = `Bearer ${token}`;
  }

  const config: RequestInit = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };

  try {
    const response = await fetch(url, config);

    // If unauthorized and we have a refresh token, try to refresh
    if (response.status === 401 && getRefreshToken()) {
      console.log('🔄 Token expired, attempting refresh...');
      const newToken = await refreshAccessToken();

      if (newToken) {
        console.log('✅ Token refreshed successfully');
        // Retry request with new token
        const newHeaders = { ...defaultHeaders, Authorization: `Bearer ${newToken}` };
        const newConfig = { ...config, headers: { ...newHeaders, ...options.headers } };
        const retryResponse = await fetch(url, newConfig);
        const retryData = await retryResponse.json();

        if (!retryResponse.ok) {
          throw new ApiError(retryResponse.status, retryData.message || 'API request failed', retryData);
        }

        return retryData;
      } else {
        console.log('❌ Token refresh failed, clearing tokens');
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
      }
    }

    const data = await response.json();

    if (!response.ok) {
      throw new ApiError(response.status, data.message || 'API request failed', data);
    }

    return data;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(0, 'Network error or server unavailable');
  }
};

// Authentication API
export const authApi = {
  requestOtp: (email: string) =>
    apiRequest('/api/auth/otp/request', {
      method: 'POST',
      body: JSON.stringify({ email }),
    }),

  register: (data: {
    email: string;
    otp: string;
    password: string;
    name: string;
    mobile_no: string;
  }) =>
    apiRequest<{ access_token: string; refresh_token: string; user: User }>('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  login: (data: { email: string; otp: string }) =>
    apiRequest<{ access_token: string; refresh_token: string; user: User }>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  logout: () =>
    apiRequest('/api/auth/logout', {
      method: 'POST',
    }),

  getProfile: () =>
    apiRequest<{ user: User }>('/api/auth/profile'),

  updateProfile: (data: Partial<User>) =>
    apiRequest<{ user: User }>('/api/auth/profile/edit', {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  // Development helper - create test user and save tokens
  createTestUser: async () => {
    const response = await fetch(`${API_BASE_URL}/api/create-test-user`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });

    if (response.ok) {
      const data = await response.json();
      if (data.success && data.data?.access_token && data.data?.refresh_token) {
        saveTokens(data.data.access_token, data.data.refresh_token);
        return data;
      }
    }

    throw new Error('Failed to create test user');
  },
};

// Courses API
export const coursesApi = {
  getAll: () =>
    apiRequest<{ courses: Course[] }>('/api/courses'),

  getById: (id: number, includeSubjects = true) =>
    apiRequest<{ course: Course }>(`/api/courses/${id}?include_subjects=${includeSubjects}`),
};

// Subjects API
export const subjectsApi = {
  getByCourse: (courseId: number) =>
    apiRequest<{ subjects: Subject[] }>(`/api/subjects?course_id=${courseId}`),

  getSubjects: (courseId: number, includeDeleted = false) =>
    apiRequest<{ subjects: Subject[] }>(`/api/subjects?course_id=${courseId}&include_deleted=${includeDeleted}`),

  getBundles: (courseId: number, includeDeleted = false) =>
    apiRequest<{ bundles: Subject[] }>(`/api/bundles?course_id=${courseId}&include_deleted=${includeDeleted}`),
};

// Community API
export const communityApi = {
  getPosts: () =>
    apiRequest<{ posts: BlogPost[] }>('/api/community/posts'),

  createPost: (data: { title: string; content: string; tags: string[] }) =>
    apiRequest<{ post: BlogPost }>('/api/community/posts', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  likePost: (postId: number) =>
    apiRequest(`/api/community/posts/${postId}/like`, {
      method: 'POST',
    }),

  addComment: (postId: number, content: string) =>
    apiRequest(`/api/community/posts/${postId}/comment`, {
      method: 'POST',
      body: JSON.stringify({ content }),
    }),

  deletePost: (postId: number) =>
    apiRequest(`/api/community/posts/${postId}`, {
      method: 'DELETE',
    }),
};

// Questions API
export const questionsApi = {
  getQuestions: (params?: { subject_id?: number; difficulty?: string; limit?: number }) => {
    const queryParams = new URLSearchParams();
    if (params?.subject_id) queryParams.append('subject_id', params.subject_id.toString());
    if (params?.difficulty) queryParams.append('difficulty', params.difficulty);
    if (params?.limit) queryParams.append('limit', params.limit.toString());

    const queryString = queryParams.toString();
    return apiRequest<{ questions: Question[] }>(`/api/questions${queryString ? `?${queryString}` : ''}`);
  },

  getById: (id: number) =>
    apiRequest<{ question: Question }>(`/api/questions/${id}`),
};

// MCQ Generation API
export interface MCQQuestion {
  question: string;
  options: string[];
  correct_answer: string;
  explanation?: string;
  difficulty?: string;
}

export interface MCQGenerationResponse {
  success: boolean;
  questions: MCQQuestion[];
  raw_response?: string;
  model_used?: string;
  sources_used?: string[];
  total_pdfs_processed?: number;
  total_sources_used_for_mcq?: number;
  error?: string;
}

export interface AIStatusResponse {
  status: string;
  dependencies: {
    sentence_transformers: boolean;
    PyPDF2: boolean;
    ollama: boolean;
    numpy: boolean;
  };
  pdf_folder: string;
  pdfs_loaded: number;
  sources: string[];
}

export const mcqGenerationApi = {
  // Check AI service status
  getAIStatus: () =>
    apiRequest<AIStatusResponse>('/api/ai/rag/status'),

  // Generate MCQ from text content (Admin only)
  generateFromText: (data: {
    content: string;
    num_questions: number;
    subject_name?: string;
    difficulty?: 'easy' | 'medium' | 'hard';
    exam_category_id?: number;
    subject_id?: number;
    save_to_database?: boolean;
  }) =>
    apiRequest<MCQGenerationResponse>('/api/ai/generate-questions-from-text', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Generate MCQ from PDFs (Admin only)
  generateFromPDFs: (data: {
    num_questions: number;
    subject_name?: string;
    difficulty?: 'easy' | 'medium' | 'hard';
    exam_category_id?: number;
    subject_id?: number;
    save_to_database?: boolean;
  }) =>
    apiRequest<MCQGenerationResponse>('/api/ai/generate-questions-from-pdfs', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // RAG Chat functionality
  ragChat: (data: {
    query: string;
    session_id?: string;
  }) =>
    apiRequest<{
      status: string;
      response: string;
      sources: string[];
      relevant_docs: number;
    }>('/api/ai/rag/chat', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Reload RAG index (Admin only)
  reloadRAGIndex: () =>
    apiRequest<{
      status: string;
      message: string;
      pdfs_loaded: number;
      sources: string[];
    }>('/api/ai/rag/reload', {
      method: 'POST',
    }),
};

// User Tests API
export const userTestsApi = {
  getAvailableTests: () => {
    const token = getAuthToken();
    // Use development endpoint if no authentication token is available
    const endpoint = token ? '/api/user/available-tests' : '/api/dev/available-tests';
    return apiRequest<{ available_tests: any[]; total_purchases: number; dev_mode?: boolean }>(endpoint);
  },

  startTest: (subjectId: number, purchaseId?: number) =>
    apiRequest<{
      test_attempt_id: number;
      subject_id: number;
      remaining_tests: number;
      message: string;
      next_step: string;
    }>('/api/user/start-test', {
      method: 'POST',
      body: JSON.stringify({
        subject_id: subjectId,
        purchase_id: purchaseId
      }),
    }),

  generateTestQuestions: (testAttemptId: number) =>
    apiRequest<{
      test_attempt_id: number;
      questions_generated: number;
      questions: Array<{
        id: number;
        question: string;
        options: { A: string; B: string; C: string; D: string };
        correct_answer: string;
        explanation: string;
      }>;
      purchase_type: 'subject' | 'bundle';
      exam_type: string;
      subject_directories_used: string[];
      sources_used: string[];
      ai_model: string;
    }>('/api/user/generate-test-questions', {
      method: 'POST',
      body: JSON.stringify({
        test_attempt_id: testAttemptId
      }),
    }),
};

// Admin API
export const adminApi = {
  // Courses management
  getCourses: () =>
    apiRequest<{ courses: Course[] }>('/api/admin/courses'),

  createCourse: (data: {
    course_name: string;
    description: string;
    amount?: number;
    offer_amount?: number;
    max_tokens?: number;
  }) =>
    apiRequest<{ course: Course }>('/api/admin/courses', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateCourse: (id: number, data: {
    course_name: string;
    description: string;
    amount?: number;
    offer_amount?: number;
    max_tokens?: number;
  }) =>
    apiRequest<{ course: Course }>(`/api/admin/courses/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  deleteCourse: (id: number) =>
    apiRequest(`/api/admin/courses/${id}`, {
      method: 'DELETE',
    }),

  // Subjects management
  getSubjects: (courseId: number, includeDeleted = false) =>
    apiRequest<{ subjects: Subject[] }>(`/api/subjects?course_id=${courseId}&include_deleted=${includeDeleted}`),

  getBundles: (courseId: number, includeDeleted = false) =>
    apiRequest<{ bundles: Subject[] }>(`/api/bundles?course_id=${courseId}&include_deleted=${includeDeleted}`),

  createSubject: (data: {
    course_id: number;
    subject_name: string;
    amount?: number;
    offer_amount?: number;
    max_tokens?: number;
    total_mock?: number;
    is_bundle?: boolean;
  }) =>
    apiRequest<{ subject: Subject }>('/api/admin/subjects', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateSubject: (id: number, data: {
    subject_name?: string;
    amount?: number;
    offer_amount?: number;
    max_tokens?: number;
    total_mock?: number;
    is_bundle?: boolean;
    is_deleted?: boolean;
  }) =>
    apiRequest<{ subject: Subject }>(`/api/admin/subjects/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  deleteSubject: (id: number) =>
    apiRequest(`/api/admin/subjects/${id}`, {
      method: 'DELETE',
    }),

  // Users management
  getUsers: () =>
    apiRequest<{ users: User[] }>('/api/admin/users'),

  // Stats
  getStats: () =>
    apiRequest<{ stats: any }>('/api/admin/stats'),

  deactivateUser: (id: number) =>
    apiRequest(`/api/admin/users/${id}/deactivate`, {
      method: 'PUT',
    }),

  getUserPurchases: (id: number) =>
    apiRequest(`/api/admin/users/${id}/purchases`),

  // Posts management
  updatePost: (id: number, data: { title: string; content: string; tags: string[] }) =>
    apiRequest(`/api/admin/posts/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  deletePost: (id: number) =>
    apiRequest(`/api/admin/posts/${id}`, {
      method: 'DELETE',
    }),
};

export default {
  auth: authApi,
  courses: coursesApi,
  subjects: subjectsApi,
  community: communityApi,
  questions: questionsApi,
  mcqGeneration: mcqGenerationApi,
  userTests: userTestsApi,
  admin: adminApi,
};
