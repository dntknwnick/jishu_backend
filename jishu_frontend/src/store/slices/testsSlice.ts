import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { questionsApi, Question, ApiError } from '../../services/api';

interface TestsState {
  questions: Question[];
  currentTest: {
    id: string | null;
    questions: Question[];
    answers: { [questionId: number]: number };
    flagged: number[];
    timeLeft: number;
    isActive: boolean;
  };
  testHistory: any[];
  isLoading: boolean;
  error: string | null;
}

const initialState: TestsState = {
  questions: [],
  currentTest: {
    id: null,
    questions: [],
    answers: {},
    flagged: [],
    timeLeft: 0,
    isActive: false,
  },
  testHistory: [],
  isLoading: false,
  error: null,
};

// Async thunks
export const fetchQuestions = createAsyncThunk(
  'tests/fetchQuestions',
  async (
    params: { subject_id?: number; difficulty?: string; limit?: number },
    { rejectWithValue }
  ) => {
    try {
      const response = await questionsApi.getQuestions(params);
      return response.data?.questions || [];
    } catch (error) {
      if (error instanceof ApiError) {
        return rejectWithValue(error.message);
      }
      return rejectWithValue('Failed to fetch questions');
    }
  }
);

const testsSlice = createSlice({
  name: 'tests',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    startTest: (state, action) => {
      const { testId, questions, duration } = action.payload;
      state.currentTest = {
        id: testId,
        questions,
        answers: {},
        flagged: [],
        timeLeft: duration,
        isActive: true,
      };
    },
    endTest: (state) => {
      state.currentTest.isActive = false;
    },
    answerQuestion: (state, action) => {
      const { questionId, answerIndex } = action.payload;
      state.currentTest.answers[questionId] = answerIndex;
    },
    toggleFlag: (state, action) => {
      const questionId = action.payload;
      const index = state.currentTest.flagged.indexOf(questionId);
      if (index > -1) {
        state.currentTest.flagged.splice(index, 1);
      } else {
        state.currentTest.flagged.push(questionId);
      }
    },
    updateTimer: (state, action) => {
      state.currentTest.timeLeft = action.payload;
    },
    submitTest: (state, action) => {
      const result = action.payload;
      state.testHistory.push(result);
      state.currentTest = {
        id: null,
        questions: [],
        answers: {},
        flagged: [],
        timeLeft: 0,
        isActive: false,
      };
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchQuestions.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchQuestions.fulfilled, (state, action) => {
        state.isLoading = false;
        state.questions = action.payload;
      })
      .addCase(fetchQuestions.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });
  },
});

export const {
  clearError,
  startTest,
  endTest,
  answerQuestion,
  toggleFlag,
  updateTimer,
  submitTest,
} = testsSlice.actions;
export default testsSlice.reducer;
