import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Layout } from './components/Layout'
import { ProtectedRoute } from './components/ProtectedRoute'
import { LoginPage } from './pages/LoginPage'
import { RegisterPage } from './pages/RegisterPage'
import { DashboardPage } from './pages/DashboardPage'
import { PoliciesPage } from './pages/PoliciesPage'
import { PolicyDetailPage } from './pages/PolicyDetailPage'
import { RenewalsPage } from './pages/RenewalsPage'
import { ChatPage } from './pages/ChatPage'
import { NotificationsPage } from './pages/NotificationsPage'
import { ProfilePage } from './pages/ProfilePage'
import { AdminPage } from './pages/AdminPage'
import { DataManagementPage } from './pages/DataManagementPage'
import { ResetPasswordPage } from './pages/ResetPasswordPage'
import { SupportPage } from './pages/SupportPage'
import { MeetingsPage } from './pages/MeetingsPage'
import { AdminMeetingsPage } from './pages/AdminMeetingsPage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="policies" element={<PoliciesPage />} />
          <Route path="policies/:id" element={<PolicyDetailPage />} />
          <Route path="renewals" element={<RenewalsPage />} />
          <Route path="chat" element={<ChatPage />} />
          <Route path="support" element={<SupportPage />} />
          <Route path="meetings" element={<MeetingsPage />} />
          <Route path="notifications" element={<NotificationsPage />} />
          <Route path="profile" element={<ProfilePage />} />
          <Route
            path="admin"
            element={
              <ProtectedRoute adminOnly>
                <AdminPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="data-management"
            element={
              <ProtectedRoute adminOnly>
                <DataManagementPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="admin/meetings"
            element={
              <ProtectedRoute adminOnly>
                <AdminMeetingsPage />
              </ProtectedRoute>
            }
          />
        </Route>
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
