//App.tsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router';
// import { AuthProvider } from '@/contexts/AuthContext';
//import ProtectedRoute from '@/components/ProtectedRoute';
import Layout from '@/components/Layout';
// import Login from '@/pages/Login';
// import Dashboard from '@/pages/Dashboard';
import Accounts from '@/pages/Accounts';
// import Categories from '@/pages/Categories';
// import Transactions from '@/pages/Transactions';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* <Route path="/login" element={<Login />} /> */}
        <Route
          path="/dashboard"
          element={
            <Layout></Layout>
          }
        />
        <Route
          path="/accounts"
          element={
            <Layout>
              <Accounts />
            </Layout>
          }
        />
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
