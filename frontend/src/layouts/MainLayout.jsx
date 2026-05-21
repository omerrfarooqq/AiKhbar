import { Outlet } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import GoldenBackground from '../components/GoldenBackground';

/** Shared page shell: background, nav, routed content and footer. */
export default function MainLayout() {
  return (
    <div className="flex min-h-screen flex-col">
      <GoldenBackground />
      <Navbar />
      <main className="flex-1">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}
