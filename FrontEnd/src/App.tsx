import { BrowserRouter, Routes, Route, Navigate } from 'react-router';
import Layout from '@/components/Layout';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/dashboard"
          element={
            <Layout></Layout>
          }
        />
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
