import { ReactNode } from 'react';
import { NavLink, useNavigate } from 'react-router';
import { LayoutDashboard, Wallet, Tag, ArrowLeftRight, LogOut } from 'lucide-react';

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const navigate = useNavigate();

  const navItems = [
    { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/', icon: Wallet, label: 'Accounts' },
    { to: '/', icon: Tag, label: 'Categories' },
    { to: '/', icon: ArrowLeftRight, label: 'Transactions' },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <aside className="fixed top-0 left-0 h-full w-64 bg-white border-r border-gray-200 z-10">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
              <Wallet className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-gray-900">My Wallet</h1>
              <p className="text-xs text-gray-500">Manager</p>
            </div>
          </div>
        </div>

        <nav className="p-4 space-y-2">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center space-x-3 px-4 py-3 rounded-lg transition ${
                  isActive
                    ? 'bg-blue-50 text-blue-600'
                    : 'text-gray-700 hover:bg-gray-100'
                }`
              }
            >
              <item.icon className="w-5 h-5" />
              <span className="font-medium">{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200">
          <button
            // onClick={handleLogout}
            className="flex items-center space-x-3 px-4 py-3 w-full text-red-600 hover:bg-red-50 rounded-lg transition"
          >
            <LogOut className="w-5 h-5" />
            <span className="font-medium">Logout</span>
          </button>
        </div>
      </aside>

      <main className="ml-64 p-8">{children}</main>
    </div>
  );
}
