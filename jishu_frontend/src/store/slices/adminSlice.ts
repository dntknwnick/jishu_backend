import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { adminApi, Course, Subject, User, ApiError } from '../../services/api';

interface AdminState {
  // Course management
  courses: Course[];
  subjects: Subject[];
  
  // User management
  users: User[];
  
  // Analytics data
  stats: {
    totalUsers: number;
    activeTests: number;
    monthlyRevenue: number;
    avgScore: number;
  };
  
  // System status
  systemStatus: {
    apiStatus: string;
    databaseStatus: string;
    serverLoad: number;
    activeSessions: number;
  };
  
  isLoading: boolean;
  error: string | null;
}

const initialState: AdminState = {
  courses: [],
  subjects: [],
  users: [],
  stats: {
    totalUsers: 0,
    activeTests: 0,
    monthlyRevenue: 0,
    avgScore: 0,
  },
  systemStatus: {
    apiStatus: 'operational',
    databaseStatus: 'healthy',
    serverLoad: 0,
    activeSessions: 0,
  },
  isLoading: false,
  error: null,
};

// Async thunks for admin operations
export const fetchUsers = createAsyncThunk(
  'admin/fetchUsers',
  async (_, { rejectWithValue }) => {
    try {
      const response = await adminApi.getUsers();
      return response.data?.users || [];
    } catch (error) {
      if (error instanceof ApiError) {
        return rejectWithValue(error.message);
      }
      return rejectWithValue('Failed to fetch users');
    }
  }
);

export const fetchCourses = createAsyncThunk(
  'admin/fetchCourses',
  async (_, { rejectWithValue }) => {
    try {
      const response = await adminApi.getCourses();
      return response.data?.courses || [];
    } catch (error) {
      if (error instanceof ApiError) {
        return rejectWithValue(error.message);
      }
      return rejectWithValue('Failed to fetch courses');
    }
  }
);

export const fetchStats = createAsyncThunk(
  'admin/fetchStats',
  async (_, { rejectWithValue }) => {
    try {
      const response = await adminApi.getStats();
      return response.data?.stats || {};
    } catch (error) {
      if (error instanceof ApiError) {
        return rejectWithValue(error.message);
      }
      return rejectWithValue('Failed to fetch stats');
    }
  }
);

export const createCourse = createAsyncThunk(
  'admin/createCourse',
  async (
    data: {
      course_name: string;
      description: string;
      amount?: number;
      offer_amount?: number;
      max_tokens?: number;
    },
    { rejectWithValue }
  ) => {
    try {
      const response = await adminApi.createCourse(data);
      return response.data?.course;
    } catch (error) {
      if (error instanceof ApiError) {
        return rejectWithValue(error.message);
      }
      return rejectWithValue('Failed to create course');
    }
  }
);

export const updateCourse = createAsyncThunk(
  'admin/updateCourse',
  async (
    { id, data }: {
      id: number;
      data: {
        course_name: string;
        description: string;
        amount?: number;
        offer_amount?: number;
        max_tokens?: number;
      }
    },
    { rejectWithValue }
  ) => {
    try {
      const response = await adminApi.updateCourse(id, data);
      return response.data?.course;
    } catch (error) {
      if (error instanceof ApiError) {
        return rejectWithValue(error.message);
      }
      return rejectWithValue('Failed to update course');
    }
  }
);

export const deleteCourse = createAsyncThunk(
  'admin/deleteCourse',
  async (id: number, { rejectWithValue }) => {
    try {
      await adminApi.deleteCourse(id);
      return id;
    } catch (error) {
      if (error instanceof ApiError) {
        return rejectWithValue(error.message);
      }
      return rejectWithValue('Failed to delete course');
    }
  }
);

export const fetchSubjects = createAsyncThunk(
  'admin/fetchSubjects',
  async (courseId: number, { rejectWithValue }) => {
    try {
      const response = await adminApi.getSubjects(courseId);
      return response.data?.subjects || [];
    } catch (error) {
      if (error instanceof ApiError) {
        return rejectWithValue(error.message);
      }
      return rejectWithValue('Failed to fetch subjects');
    }
  }
);

export const createSubject = createAsyncThunk(
  'admin/createSubject',
  async (
    data: {
      course_id: number;
      subject_name: string;
      amount?: number;
      offer_amount?: number;
      max_tokens?: number;
    },
    { rejectWithValue }
  ) => {
    try {
      const response = await adminApi.createSubject(data);
      return response.data?.subject;
    } catch (error) {
      if (error instanceof ApiError) {
        return rejectWithValue(error.message);
      }
      return rejectWithValue('Failed to create subject');
    }
  }
);

export const updateSubject = createAsyncThunk(
  'admin/updateSubject',
  async (
    { id, data }: {
      id: number;
      data: {
        subject_name?: string;
        amount?: number;
        offer_amount?: number;
        max_tokens?: number;
      }
    },
    { rejectWithValue }
  ) => {
    try {
      const response = await adminApi.updateSubject(id, data);
      return response.data?.subject;
    } catch (error) {
      if (error instanceof ApiError) {
        return rejectWithValue(error.message);
      }
      return rejectWithValue('Failed to update subject');
    }
  }
);

export const deleteSubject = createAsyncThunk(
  'admin/deleteSubject',
  async (id: number, { rejectWithValue }) => {
    try {
      await adminApi.deleteSubject(id);
      return id;
    } catch (error) {
      if (error instanceof ApiError) {
        return rejectWithValue(error.message);
      }
      return rejectWithValue('Failed to delete subject');
    }
  }
);

export const deactivateUser = createAsyncThunk(
  'admin/deactivateUser',
  async (id: number, { rejectWithValue }) => {
    try {
      await adminApi.deactivateUser(id);
      return id;
    } catch (error) {
      if (error instanceof ApiError) {
        return rejectWithValue(error.message);
      }
      return rejectWithValue('Failed to deactivate user');
    }
  }
);

const adminSlice = createSlice({
  name: 'admin',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    setStats: (state, action) => {
      state.stats = action.payload;
    },
    setSystemStatus: (state, action) => {
      state.systemStatus = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch users
      .addCase(fetchUsers.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchUsers.fulfilled, (state, action) => {
        state.isLoading = false;
        state.users = action.payload;
      })
      .addCase(fetchUsers.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })

      // Fetch courses
      .addCase(fetchCourses.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchCourses.fulfilled, (state, action) => {
        state.isLoading = false;
        state.courses = action.payload;
      })
      .addCase(fetchCourses.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })

      // Fetch stats
      .addCase(fetchStats.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchStats.fulfilled, (state, action) => {
        state.isLoading = false;
        state.stats = action.payload;
      })
      .addCase(fetchStats.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })

      // Create course
      .addCase(createCourse.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(createCourse.fulfilled, (state, action) => {
        state.isLoading = false;
        if (action.payload) {
          state.courses.push(action.payload);
        }
      })
      .addCase(createCourse.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      
      // Update course
      .addCase(updateCourse.fulfilled, (state, action) => {
        if (action.payload) {
          const index = state.courses.findIndex(c => c.id === action.payload!.id);
          if (index !== -1) {
            state.courses[index] = action.payload;
          }
        }
      })
      .addCase(updateCourse.rejected, (state, action) => {
        state.error = action.payload as string;
      })
      
      // Delete course
      .addCase(deleteCourse.fulfilled, (state, action) => {
        state.courses = state.courses.filter(c => c.id !== action.payload);
      })
      .addCase(deleteCourse.rejected, (state, action) => {
        state.error = action.payload as string;
      })
      
      // Fetch subjects
      .addCase(fetchSubjects.fulfilled, (state, action) => {
        state.subjects = action.payload;
      })
      .addCase(fetchSubjects.rejected, (state, action) => {
        state.error = action.payload as string;
      })

      // Create subject
      .addCase(createSubject.fulfilled, (state, action) => {
        if (action.payload) {
          state.subjects.push(action.payload);
        }
      })
      .addCase(createSubject.rejected, (state, action) => {
        state.error = action.payload as string;
      })

      // Update subject
      .addCase(updateSubject.fulfilled, (state, action) => {
        if (action.payload) {
          const index = state.subjects.findIndex(s => s.id === action.payload!.id);
          if (index !== -1) {
            state.subjects[index] = action.payload;
          }
        }
      })
      .addCase(updateSubject.rejected, (state, action) => {
        state.error = action.payload as string;
      })

      // Delete subject
      .addCase(deleteSubject.fulfilled, (state, action) => {
        state.subjects = state.subjects.filter(s => s.id !== action.payload);
      })
      .addCase(deleteSubject.rejected, (state, action) => {
        state.error = action.payload as string;
      })
      
      // Deactivate user
      .addCase(deactivateUser.fulfilled, (state, action) => {
        const userId = action.payload;
        const user = state.users.find(u => u.id === userId);
        if (user) {
          user.status = 'inactive';
        }
      })
      .addCase(deactivateUser.rejected, (state, action) => {
        state.error = action.payload as string;
      });
  },
});

export const { clearError, setStats, setSystemStatus } = adminSlice.actions;
export default adminSlice.reducer;
