import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { subjectsApi, Subject, ApiError } from '../../services/api';

interface SubjectsState {
  subjects: Subject[];
  bundles: Subject[];
  selectedSubjects: number[];
  isLoading: boolean;
  error: string | null;
}

const initialState: SubjectsState = {
  subjects: [],
  bundles: [],
  selectedSubjects: [],
  isLoading: false,
  error: null,
};

// Async thunks
export const fetchSubjectsByCourse = createAsyncThunk(
  'subjects/fetchSubjectsByCourse',
  async (courseId: number, { rejectWithValue }) => {
    try {
      const response = await subjectsApi.getSubjects(courseId);
      return response.data?.subjects || [];
    } catch (error) {
      if (error instanceof ApiError) {
        return rejectWithValue(error.message);
      }
      return rejectWithValue('Failed to fetch subjects');
    }
  }
);

export const fetchBundlesByCourse = createAsyncThunk(
  'subjects/fetchBundlesByCourse',
  async (courseId: number, { rejectWithValue }) => {
    try {
      const response = await subjectsApi.getBundles(courseId);
      return response.data?.bundles || [];
    } catch (error) {
      if (error instanceof ApiError) {
        return rejectWithValue(error.message);
      }
      return rejectWithValue('Failed to fetch bundles');
    }
  }
);

const subjectsSlice = createSlice({
  name: 'subjects',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    toggleSubjectSelection: (state, action) => {
      const subjectId = action.payload;
      const index = state.selectedSubjects.indexOf(subjectId);
      if (index > -1) {
        state.selectedSubjects.splice(index, 1);
      } else {
        state.selectedSubjects.push(subjectId);
      }
    },
    clearSelectedSubjects: (state) => {
      state.selectedSubjects = [];
    },
    setSelectedSubjects: (state, action) => {
      state.selectedSubjects = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchSubjectsByCourse.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchSubjectsByCourse.fulfilled, (state, action) => {
        state.isLoading = false;
        state.subjects = action.payload;
      })
      .addCase(fetchSubjectsByCourse.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      .addCase(fetchBundlesByCourse.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchBundlesByCourse.fulfilled, (state, action) => {
        state.isLoading = false;
        state.bundles = action.payload;
      })
      .addCase(fetchBundlesByCourse.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });
  },
});

export const { 
  clearError, 
  toggleSubjectSelection, 
  clearSelectedSubjects, 
  setSelectedSubjects 
} = subjectsSlice.actions;
export default subjectsSlice.reducer;
