import { apiClient } from './apiClient';

/** News, story-cluster, brief, chat and TTS API calls. */
export const newsService = {
  listNews: (params) =>
    apiClient.get('/news', { params }).then((r) => r.data),

  getArticle: (id) => apiClient.get(`/news/${id}`).then((r) => r.data),

  getCategories: () =>
    apiClient.get('/news/categories').then((r) => r.data),

  triggerScrape: () => apiClient.post('/news/scrape').then((r) => r.data),

  listStories: (params) =>
    apiClient.get('/stories', { params }).then((r) => r.data),

  getTopStories: (params) =>
    apiClient.get('/stories/top', { params }).then((r) => r.data),

  getStory: (id) => apiClient.get(`/stories/${id}`).then((r) => r.data),

  summarizeStory: (id, body) =>
    apiClient.post(`/stories/${id}/summary`, body).then((r) => r.data),

  getOpinions: (id) =>
    apiClient.post(`/stories/${id}/opinions`).then((r) => r.data),

  getTimeline: (id) =>
    apiClient.post(`/stories/${id}/timeline`).then((r) => r.data),

  generateDailyBrief: (body) =>
    apiClient.post('/briefs/daily', body).then((r) => r.data),

  audioDigest: () =>
    apiClient.post('/briefs/audio-digest').then((r) => r.data),

  ask: (body) => apiClient.post('/chat', body).then((r) => r.data),

  synthesize: (body) =>
    apiClient.post('/tts/synthesize', body).then((r) => r.data),
};
