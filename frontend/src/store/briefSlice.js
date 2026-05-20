import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { newsService } from '../services/newsService';

/** Generate the one-click daily brief (top stories + summaries + Urdu audio). */
export const generateBrief = createAsyncThunk(
  'brief/generate',
  async (body) => newsService.generateDailyBrief(body),
);

const briefSlice = createSlice({
  name: 'brief',
  initialState: {
    data: null,
    status: 'idle',
    error: null,
  },
  reducers: {
    clearBrief(state) {
      state.data = null;
      state.status = 'idle';
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(generateBrief.pending, (state) => {
        state.status = 'loading';
        state.error = null;
      })
      .addCase(generateBrief.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.data = action.payload;
      })
      .addCase(generateBrief.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.error.message;
      });
  },
});

export const { clearBrief } = briefSlice.actions;
export default briefSlice.reducer;
