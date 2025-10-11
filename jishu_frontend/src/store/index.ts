import { configureStore } from '@reduxjs/toolkit';
import { TypedUseSelectorHook, useDispatch, useSelector } from 'react-redux';

// Import slices (will be created in subsequent tasks)
import authSlice from './slices/authSlice';
import coursesSlice from './slices/coursesSlice';
import subjectsSlice from './slices/subjectsSlice';
import communitySlice from './slices/communitySlice';
import testsSlice from './slices/testsSlice';
import purchaseSlice from './slices/purchaseSlice';
import adminSlice from './slices/adminSlice';

export const store = configureStore({
  reducer: {
    auth: authSlice,
    courses: coursesSlice,
    subjects: subjectsSlice,
    community: communitySlice,
    tests: testsSlice,
    purchase: purchaseSlice,
    admin: adminSlice,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE'],
      },
    }),
  devTools: process.env.NODE_ENV !== 'production',
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

// Typed hooks for use throughout the app
export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

export default store;
