import { configureStore } from '@reduxjs/toolkit';
import newsReducer from './newsSlice';
import briefReducer from './briefSlice';

export const store = configureStore({
  reducer: {
    news: newsReducer,
    brief: briefReducer,
  },
});
