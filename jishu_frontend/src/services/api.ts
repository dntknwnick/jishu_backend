// API Service Layer for Jishu Backend Integration
import { API_BASE_URL } from '../config/environment';

// Request deduplication and queuing system
class RequestManager {
  private pendingRequests = new Map<string, Promise<any>>();
  private refreshPromise: Promise<string | null> | null = null;
  private requestQueue: Array<() => Promise<any>> = [];
  private isRefreshing = false;

  // Generate unique key for request deduplication
  private getRequestKey(endpoint: string, options: RequestInit): string {
    const method = options.method || 'GET';
    const body = options.body || '';
    return `${method}:${endpoint}:${body}`;
  }

  // Check if request is already pending
  isDuplicateRequest(endpoint: string, options: RequestInit): boolean {
    const key = this.getRequestKey(endpoint, options);
    return this.pendingRequests.has(key);
  }

  // Get existing pending request
  getPendingRequest(endpoint: string, options: RequestInit): Promise<any> | null {
    const key = this.getRequestKey(endpoint, options);
    return this.pendingRequests.get(key) || null;
  }

  // Add request to pending map
  addPendingRequest(endpoint: string, options: RequestInit, promise: Promise<any>): void {
    const key = this.getRequestKey(endpoint, options);
    this.pendingRequests.set(key, promise);

    // Clean up when request completes
    promise.finally(() => {
      this.pendingRequests.delete(key);
    });
  }

  // Centralized token refresh with queuing
  async refreshToken(): Promise<string | null> {
    if (this.refreshPromise) {
      return this.refreshPromise;
    }

    this.isRefreshing = true;
    this.refreshPromise = this.performTokenRefresh();

    try {
      const result = await this.refreshPromise;

      // Process queued requests
      if (result) {
        const queuedRequests = [...this.requestQueue];
        this.requestQueue = [];

        // Execute all queued requests
        await Promise.all(queuedRequests.map(request => request()));
      }

      return result;
    } finally {
      this.refreshPromise = null;
      this.isRefreshing = false;
    }
  }

  private async performTokenRefresh(): Promise<string | null> {
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
  }

  // Add request to queue during token refresh
  queueRequest(requestFn: () => Promise<any>): Promise<any> {
    return new Promise((resolve, reject) => {
      this.requestQueue.push(async () => {
        try {
          const result = await requestFn();
          resolve(result);
        } catch (error) {
          reject(error);
        }
      });
    });
  }

  // Check if currently refreshing token
  isTokenRefreshing(): boolean {
    return this.isRefreshing;
  }
}

const requestManager = new RequestManager();

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
  is_deleted?: boolean;
  amount?: number;
  offer_amount?: number;
  max_tokens?: number;
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
  image_url?: string;
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
  recent_comments?: BlogComment[];
  image?: string; // For backward compatibility
}

export interface BlogComment {
  id: number;
  user_id: number;
  post_id: number;
  parent_comment_id?: number;
  content: string;
  likes_count: number;
  is_deleted: boolean;
  created_at: string;
  updated_at: string;
  user?: {
    id: number;
    name: string;
    email_id: string;
  };
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

// Legacy refresh function - now uses RequestManager
const refreshAccessToken = async (): Promise<string | null> => {
  return requestManager.refreshToken();
};

// Generic API request function with duplicate protection
export const apiRequest = async <T = any>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> => {
  // Check for duplicate requests (except for certain endpoints)
  const allowDuplicates = ['/api/auth/otp/request', '/api/ai/chat', '/api/ai/rag/chat'].some(path => endpoint.includes(path));

  if (!allowDuplicates && requestManager.isDuplicateRequest(endpoint, options)) {
    console.log('🔄 Duplicate request detected, returning existing promise');
    return requestManager.getPendingRequest(endpoint, options);
  }

  // If token is being refreshed, queue this request
  if (requestManager.isTokenRefreshing() && getAuthToken()) {
    console.log('🔄 Token refresh in progress, queueing request');
    return requestManager.queueRequest(() => apiRequest(endpoint, options));
  }

  const requestPromise = performApiRequest<T>(endpoint, options);

  // Track this request for deduplication
  if (!allowDuplicates) {
    requestManager.addPendingRequest(endpoint, options, requestPromise);
  }

  return requestPromise;
};

// Actual API request implementation
const performApiRequest = async <T = any>(
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
      const newToken = await requestManager.refreshToken();

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

// Profile API
export const profileApi = {
  // Get comprehensive user profile
  getProfile: () =>
    apiRequest<{ user: User }>('/api/user/profile'),

  // Update user personal information
  updateProfile: (data: Partial<User>) =>
    apiRequest<{ user: User }>('/api/user/profile', {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  // Get user statistics
  getStats: () =>
    apiRequest<{ stats: any }>('/api/user/stats'),

  // Get user academic information
  getAcademics: () =>
    apiRequest<{ academics: any }>('/api/user/academics'),

  // Update user academic information
  updateAcademics: (data: any) =>
    apiRequest<{ academics: any }>('/api/user/academics', {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  // Get user purchase history
  getPurchases: () =>
    apiRequest<{ purchases: any[] }>('/api/user/purchases'),
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

// Purchase API - Enhanced for Mock Test Flow
export const purchaseApi = {
  // Create a new purchase with enhanced options
  createPurchase: (data: {
    course_id: number;
    purchase_type: 'single_subject' | 'multiple_subjects' | 'full_bundle';
    subject_id?: number;      // For single_subject
    subject_ids?: number[];   // For multiple_subjects and full_bundle
    cost: number;
  }) =>
    apiRequest<{
      purchase_id: number;
      purchase_type: string;
      subjects_included: number[];
      test_cards_created: number;
      total_test_cards: number;
      chatbot_tokens_unlimited: boolean;
      message: string;
    }>('/api/purchases', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Get user's purchases
  getUserPurchases: () =>
    apiRequest<{
      purchases: Array<{
        id: number;
        exam_category_id: number;
        exam_category_name: string;
        purchase_type: string;
        subjects_included: number[];
        cost: number;
        purchase_date: string;
        status: string;
        test_cards_count: number;
        chatbot_tokens_unlimited: boolean;
      }>;
      total_purchases: number;
    }>('/api/user/purchases'),
};

// Community API
export const communityApi = {
  getPosts: () =>
    apiRequest<{ posts: BlogPost[] }>('/api/community/posts'),

  createPost: (data: { title: string; content: string; tags: string[]; image?: File }) => {
    if (data.image) {
      // Use FormData for file upload
      const formData = new FormData();
      formData.append('title', data.title);
      formData.append('content', data.content);
      formData.append('tags', data.tags.join(','));
      formData.append('image', data.image);

      return apiRequest<{ post: BlogPost }>('/api/community/posts', {
        method: 'POST',
        body: formData,
        // Don't set Content-Type header, let browser set it for FormData
        headers: {},
      });
    } else {
      // Use JSON for posts without images
      return apiRequest<{ post: BlogPost }>('/api/community/posts', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    }
  },

  likePost: (postId: number) =>
    apiRequest<{
      liked: boolean;
      likes_count: number;
    }>(`/api/community/posts/${postId}/like`, {
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

// New RAG-based MCQ Generation API
export interface MCQQuestion {
  question: string;
  option_a: string;
  option_b: string;
  option_c: string;
  option_d: string;
  correct_answer: string;
  explanation?: string;
  difficulty?: string;
}

export interface MCQGenerationResponse {
  success: boolean;
  questions: MCQQuestion[];
  total_generated: number;
  subject: string;
  difficulty: string;
  generation_time: number;
  sources_used: string[];
  model_used: string;
  saved_to_database: boolean;
  method: string;
  error?: string;
}

export interface ChatbotResponse {
  success: boolean;
  response: string;
  sources: string[];
  relevant_docs: number;
  session_id: string;
  response_time: number;
  model_used: string;
  method: string;
  error?: string;
}

export interface RAGStatusResponse {
  system_status: string;
  dependencies: {
    chromadb: boolean;
    sentence_transformers: boolean;
    pypdf2: boolean;
    ollama: boolean;
  };
  configuration: {
    pdf_folder_path: string;
    vector_store_path: string;
    ollama_model: string;
    embedding_model: string;
  };
  vector_stores: {
    [subject: string]: {
      available: boolean;
      document_count: number;
      status: string;
    };
  };
  subjects_available: string[];
  health: string;
}

export const mcqGenerationApi = {
  // Check RAG system status
  getRAGStatus: () =>
    apiRequest<RAGStatusResponse>('/api/rag/status'),

  // Generate MCQ using new RAG pipeline
  generate: (data: {
    subject: string;
    num_questions: number;
    difficulty: string;
  }) =>
    apiRequest<MCQGenerationResponse>('/api/mcq/generate', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Initialize RAG system (Admin only)
  initializeRAG: (data?: {
    force_recreate?: boolean;
  }) =>
    apiRequest<{
      message: string;
      successful_subjects: string[];
      total_subjects: number;
      successful_count: number;
      results: { [subject: string]: boolean };
    }>('/api/rag/initialize', {
      method: 'POST',
      body: JSON.stringify(data || {}),
    }),

  // Reload specific subject vector store (Admin only)
  reloadSubject: (subject: string) =>
    apiRequest<{
      message: string;
      subject: string;
    }>(`/api/rag/reload/${subject}`, {
      method: 'POST',
    }),
};

// New Chatbot API
export const chatbotApi = {
  // Send query to chatbot using RAG pipeline
  query: (data: {
    query: string;
    subject?: string;
    session_id?: string;
  }) =>
    apiRequest<ChatbotResponse>('/api/chatbot/query', {
      method: 'POST',
      body: JSON.stringify(data),
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

  // Generate questions for test session (new test card system)
  generateTestQuestionsForSession: (sessionId: number) =>
    apiRequest<{
      session_id: number;
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
        session_id: sessionId
      }),
    }),

  // Chunked MCQ Generation API methods
  startChunkedGeneration: (data: { test_attempt_id?: number; session_id?: number }) =>
    apiRequest<{
      success: boolean;
      generation_id: string;
      initial_questions: Array<{
        id: number;
        question: string;
        options: { A: string; B: string; C: string; D: string };
        correct_answer: string;
        explanation: string;
      }>;
      progress: {
        generation_id: string;
        total_questions_needed: number;
        questions_generated_count: number;
        generation_status: string;
        progress_percentage: number;
      };
      total_questions_needed: number;
      questions_ready: number;
      background_generation_started: boolean;
    }>('/api/user/generate-test-questions-chunked', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  getGenerationProgress: (generationId: string) =>
    apiRequest<{
      success: boolean;
      progress: {
        generation_id: string;
        total_questions_needed: number;
        questions_generated_count: number;
        generation_status: string;
        progress_percentage: number;
        error_message?: string;
      };
      questions: Array<{
        id: number;
        question: string;
        options: { A: string; B: string; C: string; D: string };
        correct_answer: string;
        explanation: string;
      }>;
      is_complete: boolean;
      has_error: boolean;
    }>(`/api/user/mcq-generation-progress/${generationId}`),

  getAllGeneratedQuestions: (generationId: string) =>
    apiRequest<{
      success: boolean;
      questions: Array<{
        id: number;
        question: string;
        options: { A: string; B: string; C: string; D: string };
        correct_answer: string;
        explanation: string;
      }>;
      total_generated: number;
      progress: {
        generation_id: string;
        total_questions_needed: number;
        questions_generated_count: number;
        generation_status: string;
        progress_percentage: number;
      };
    }>(`/api/user/mcq-generation-questions/${generationId}`),

  cancelGeneration: (generationId: string) =>
    apiRequest<{
      success: boolean;
      message: string;
    }>(`/api/user/mcq-generation-cancel/${generationId}`, {
      method: 'POST',
    }),



  // New Mock Test Card System
  getTestCards: (subjectId?: number) => {
    const params = subjectId ? `?subject_id=${subjectId}` : '';
    return apiRequest<{
      test_cards_by_subject: Array<{
        subject_id: number;
        subject_name: string;
        course_name: string;
        total_cards: number;
        available_cards: number;
        completed_cards: number;
        disabled_cards: number;
        cards: Array<{
          id: number;
          purchase_id: number;
          test_number: number;
          max_attempts: number;
          attempts_used: number;
          remaining_attempts: number;
          questions_generated: boolean;
          latest_score: number;
          latest_percentage: number;
          latest_attempt_date: string | null;
          status: 'available' | 'in_progress' | 'completed' | 'disabled';
          is_available: boolean;
        }>;
      }>;
      total_subjects: number;
    }>(`/api/user/test-cards${params}`);
  },

  // Start a test attempt for a specific test card
  startTestCard: (mockTestId: number) =>
    apiRequest<{
      session_id: number;
      mock_test_id: number;
      attempt_number: number;
      remaining_attempts: number;
      questions_generated: boolean;
    }>(`/api/user/test-cards/${mockTestId}/start`, {
      method: 'POST',
    }),

  // Get questions for a test session (generates on first attempt, reuses on re-attempts)
  getTestQuestions: (sessionId: number) =>
    apiRequest<{
      questions: Array<{
        id: number;
        question: string;
        option_1: string;
        option_2: string;
        option_3: string;
        option_4: string;
        explanation?: string;
      }>;
      session_id: number;
      mock_test_id: number;
      attempt_number: number;
      is_re_attempt: boolean;
      total_questions: number;
      generation_info?: {
        model_used: string;
        sources_used: string[];
      };
    }>(`/api/user/test-sessions/${sessionId}/questions`),

  // Submit test session answers
  submitTestSession: (sessionId: number, answers: any[], timeTaken: number) =>
    apiRequest<{
      session_id: number;
      mock_test_id: number;
      score: number;
      percentage: number;
      attempt_number: number;
      remaining_attempts: number;
      is_final_attempt: boolean;
    }>(`/api/user/test-sessions/${sessionId}/submit`, {
      method: 'POST',
      body: JSON.stringify({
        answers,
        time_taken: timeTaken,
      }),
    }),

  // Get test analytics (based on latest attempts only)
  getTestAnalytics: (subjectId?: number) => {
    const params = subjectId ? `?subject_id=${subjectId}` : '';
    return apiRequest<{
      total_tests_taken: number;
      average_score: number;
      average_percentage: number;
      best_score: number;
      worst_score: number;
      total_time_spent: number;
      improvement_data: {
        improvement_available: boolean;
        first_attempt_average?: number;
        latest_attempt_average?: number;
        improvement_points?: number;
        improvement_percentage?: number;
      };
    }>(`/api/user/test-analytics${params}`);
  },
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
    is_deleted?: boolean;
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
  getUsers: (page = 1, perPage = 10, search = '', status = '', isPremium = '') => {
    const params = new URLSearchParams();
    params.append('page', page.toString());
    params.append('per_page', perPage.toString());
    if (search) params.append('search', search);
    if (status) params.append('status', status);
    if (isPremium) params.append('is_premium', isPremium);

    return apiRequest<{
      users: Array<{
        id: number;
        name: string;
        email_id: string;
        mobile_no: string | null;
        is_premium: boolean;
        is_admin: boolean;
        status: string;
        source: string;
        google_id: string | null;
        auth_provider: string;
        created_at: string;
        last_login: string | null;
      }>;
      pagination: {
        page: number;
        pages: number;
        total: number;
        per_page: number;
      };
    }>(`/api/admin/users?${params.toString()}`);
  },

  // Stats
  getStats: () =>
    apiRequest<{
      stats: {
        totalUsers: number;
        activeUsers: number;
        totalCourses: number;
        totalSubjects: number;
        totalPosts: number;
        publishedPosts: number;
        totalPurchases: number;
        totalRevenue: number;
        totalAIQueries: number;
        totalTokensUsed: number;
        averageScore: number;
        recentUsers: Array<{
          id: number;
          name: string;
          email_id: string;
          created_at: string;
        }>;
        recentPosts: Array<{
          id: number;
          title: string;
          author_id: number;
          created_at: string;
        }>;
        totalTests: number;
        monthlyRevenue: number;
      };
    }>('/api/admin/stats'),

  deactivateUser: (id: number) =>
    apiRequest<{ user: User }>(`/api/admin/users/${id}/deactivate`, {
      method: 'PUT',
    }),

  getUserPurchases: (id: number, page = 1, perPage = 10) =>
    apiRequest<{
      purchases: Array<{
        id: number;
        user_id: number;
        exam_category_id: number;
        subject_id: number | null;
        cost: number;
        total_marks: number;
        marks_scored: number;
        total_mock_tests: number;
        mock_tests_used: number;
        purchase_type: string;
        purchase_date: string;
      }>;
      pagination: {
        page: number;
        pages: number;
        total: number;
        per_page: number;
      };
    }>(`/api/admin/users/${id}/purchases?page=${page}&per_page=${perPage}`),

  // Posts management
  getPosts: (page = 1, perPage = 10, search = '', status = '', isDeleted?: boolean) => {
    const params = new URLSearchParams();
    params.append('page', page.toString());
    params.append('per_page', perPage.toString());
    if (search) params.append('search', search);
    if (status) params.append('status', status);
    if (isDeleted !== undefined) params.append('is_deleted', isDeleted.toString());

    return apiRequest<{
      posts: Array<{
        id: number;
        title: string;
        content: string;
        user_id: number;
        user: { id: number; name: string; email_id: string };
        likes_count: number;
        comments_count: number;
        is_featured: boolean;
        is_deleted: boolean;
        status: string;
        created_at: string;
        updated_at: string;
      }>;
      pagination: {
        page: number;
        pages: number;
        total: number;
        per_page: number;
      };
    }>(`/api/admin/posts?${params.toString()}`);
  },

  getComments: (page = 1, perPage = 10, search = '', isDeleted?: boolean) => {
    const params = new URLSearchParams();
    params.append('page', page.toString());
    params.append('per_page', perPage.toString());
    if (search) params.append('search', search);
    if (isDeleted !== undefined) params.append('is_deleted', isDeleted.toString());

    return apiRequest<{
      comments: Array<{
        id: number;
        content: string;
        user_id: number;
        post_id: number;
        user: { id: number; name: string; email_id: string };
        post: { id: number; title: string };
        likes_count: number;
        is_deleted: boolean;
        created_at: string;
        updated_at: string;
      }>;
      pagination: {
        page: number;
        pages: number;
        total: number;
        per_page: number;
      };
    }>(`/api/admin/comments?${params.toString()}`);
  },

  updatePost: (id: number, data: { title?: string; content?: string; tags?: string[]; status?: string; is_featured?: boolean }) =>
    apiRequest<{ post: any }>(`/api/admin/posts/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  deletePost: (id: number) =>
    apiRequest<{ message: string }>(`/api/admin/posts/${id}`, {
      method: 'DELETE',
    }),

  updateComment: (id: number, data: { content: string }) =>
    apiRequest<{ comment: any }>(`/api/admin/comments/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  deleteComment: (id: number) =>
    apiRequest<{ message: string }>(`/api/admin/comments/${id}`, {
      method: 'DELETE',
    }),
};

export default {
  auth: authApi,
  courses: coursesApi,
  subjects: subjectsApi,
  purchase: purchaseApi,
  community: communityApi,
  questions: questionsApi,
  mcqGeneration: mcqGenerationApi,
  chatbot: chatbotApi,
  userTests: userTestsApi,
  admin: adminApi,
};
