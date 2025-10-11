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

export const createCourse = createAsyncThunk(
  'admin/createCourse',
  async (
    data: { course_name: string; description: string },
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
    { id, data }: { id: number; data: { course_name: string; description: string } },
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

export const createSubject = createAsyncThunk(
  'admin/createSubject',
  async (
    data: { exam_category_id: number; subject_name: string },
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
          const index = state.courses.findIndex(c => c.id === action.payload.id);
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
      
      // Create subject
      .addCase(createSubject.fulfilled, (state, action) => {
        if (action.payload) {
          state.subjects.push(action.payload);
        }
      })
      .addCase(createSubject.rejected, (state, action) => {
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
