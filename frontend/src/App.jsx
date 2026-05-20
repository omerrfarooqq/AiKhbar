import { Routes, Route } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';
import LandingPage from './pages/LandingPage';
import NewsPage from './pages/NewsPage';
import StoryDetailPage from './pages/StoryDetailPage';
import DailyBriefPage from './pages/DailyBriefPage';
import ChatPage from './pages/ChatPage';
import NotFoundPage from './pages/NotFoundPage';

/** Application route table. */
export default function App() {
  return (
    <Routes>
      <Route element={<MainLayout />}>
        <Route index element={<LandingPage />} />
        <Route path="news" element={<NewsPage />} />
        <Route path="story/:id" element={<StoryDetailPage />} />
        <Route path="brief" element={<DailyBriefPage />} />
        <Route path="chat" element={<ChatPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}
