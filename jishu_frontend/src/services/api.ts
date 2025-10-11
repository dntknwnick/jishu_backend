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
  created_at: string;
}

export interface BlogPost {
  id: number;
  title: string;
  content: string;
  tags: string[];
  author_id: number;
  author_name: string;
  created_at: string;
  likes_count: number;
  comments_count: number;
  is_liked?: boolean;
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

  login: (data: { email: string; password: string }) =>
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
    apiRequest('/api/community/posts/${postId}/comment', {
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

// Admin API
export const adminApi = {
  // Courses management
  createCourse: (data: { course_name: string; description: string }) =>
    apiRequest<{ course: Course }>('/api/admin/courses', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateCourse: (id: number, data: { course_name: string; description: string }) =>
    apiRequest<{ course: Course }>(`/api/admin/courses/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  deleteCourse: (id: number) =>
    apiRequest(`/api/admin/courses/${id}`, {
      method: 'DELETE',
    }),

  // Subjects management
  createSubject: (data: { exam_category_id: number; subject_name: string }) =>
    apiRequest<{ subject: Subject }>('/api/admin/subjects', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateSubject: (id: number, data: { subject_name: string }) =>
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
  admin: adminApi,
};
