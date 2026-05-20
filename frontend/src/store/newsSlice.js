import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { newsService } from '../services/newsService';

/** Fetch a (filtered) page of news articles. */
export const fetchNews = createAsyncThunk(
  'news/fetch',
  async (params) => newsService.listNews(params),
);

/** Fetch top story clusters. */
export const fetchTopStories = createAsyncThunk(
  'news/fetchTop',
  async (params) => newsService.getTopStories(params),
);

const newsSlice = createSlice({
  name: 'news',
  initialState: {
    articles: [],
    total: 0,
    topStories: [],
    activeCategory: null,
    status: 'idle', // idle | loading | succeeded | failed
    error: null,
  },
  reducers: {
    setCategory(state, action) {
      state.activeCategory = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchNews.pending, (state) => {
        state.status = 'loading';
        state.error = null;
      })
      .addCase(fetchNews.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.articles = action.payload.items;
        state.total = action.payload.total;
      })
      .addCase(fetchNews.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.error.message;
      })
      .addCase(fetchTopStories.fulfilled, (state, action) => {
        state.topStories = action.payload;
      });
  },
});

export const { setCategory } = newsSlice.actions;
export default newsSlice.reducer;
