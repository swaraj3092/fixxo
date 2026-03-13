import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import StatsCards from '../components/StatsCards';
import StudentTable from '../components/StudentTable';
import ComplaintTable from '../components/ComplaintTable';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

export default function AdminDashboard() {
  const [activeTab, setActiveTab] = useState('overview');
  const [stats, setStats] = useState(null);
  const [students, setStudents] = useState([]);
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    // Check if admin is logged in
    const admin = localStorage.getItem('admin');
    if (!admin) {
      navigate('/admin/login');
      return;
    }

    fetchDashboardData();
  }, [navigate]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Fetch stats
      const statsRes = await axios.get(`${API_URL}/api/admin/stats`, { withCredentials: true });
      setStats(statsRes.data);

      // Fetch students
      const studentsRes = await axios.get(`${API_URL}/api/admin/students`, { withCredentials: true });
      setStudents(studentsRes.data);

      // Fetch complaints
      const complaintsRes = await axios.get(`${API_URL}/api/admin/complaints`, { withCredentials: true });
      setComplaints(complaintsRes.data);

    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      if (err.response?.status === 401) {
        navigate('/admin/login');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await axios.post(`${API_URL}/api/admin/logout`, {}, { withCredentials: true });
      localStorage.removeItem('admin');
      navigate('/admin/login');
    } catch (err) {
      console.error('Logout error:', err);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4 animate-spin">⚙️</div>
          <p className="text-white text-xl">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800">
      {/* Header */}
      <header className="bg-gray-800/50 backdrop-blur-lg border-b border-gray-700 sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <h1 className="text-3xl font-bold text-white">🏠 Fixxo Admin</h1>
              <span className="bg-purple-500/20 text-purple-300 px-3 py-1 rounded-full text-sm font-semibold">
                Live Dashboard
              </span>
            </div>
            <button
              onClick={handleLogout}
              className="bg-red-500/20 hover:bg-red-500/30 text-red-300 px-4 py-2 rounded-lg transition flex items-center space-x-2"
            >
              <span>🚪</span>
              <span>Logout</span>
            </button>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="bg-gray-800/30 border-b border-gray-700">
        <div className="container mx-auto px-4">
          <div className="flex space-x-1">
            {[
              { id: 'overview', label: '📊 Overview', icon: '📊' },
              { id: 'students', label: '👥 Students', icon: '👥' },
              { id: 'complaints', label: '🎫 Complaints', icon: '🎫' }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-6 py-3 font-semibold transition-all ${
                  activeTab === tab.id
                    ? 'text-white border-b-2 border-purple-500 bg-gray-800/50'
                    : 'text-gray-400 hover:text-white hover:bg-gray-800/30'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        {activeTab === 'overview' && (
          <div>
            <StatsCards stats={stats} />
            
            {/* Recent Activity */}
            <div className="mt-8 bg-gray-800/50 backdrop-blur-lg rounded-2xl border border-gray-700 p-6">
              <h2 className="text-2xl font-bold text-white mb-4">Recent Complaints</h2>
              <ComplaintTable complaints={complaints.slice(0, 5)} compact={true} />
            </div>
          </div>
        )}

        {activeTab === 'students' && (
          <div className="bg-gray-800/50 backdrop-blur-lg rounded-2xl border border-gray-700 p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-white">Registered Students</h2>
              <div className="text-gray-400">
                Total: <span className="text-white font-bold">{students.length}</span>
              </div>
            </div>
            <StudentTable students={students} onRefresh={fetchDashboardData} />
          </div>
        )}

        {activeTab === 'complaints' && (
          <div className="bg-gray-800/50 backdrop-blur-lg rounded-2xl border border-gray-700 p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-white">All Complaints</h2>
              <div className="flex space-x-4 text-sm">
                <button className="text-yellow-400 hover:text-yellow-300">
                  ⏳ Pending: {complaints.filter(c => c.status === 'PENDING').length}
                </button>
                <button className="text-green-400 hover:text-green-300">
                  ✅ Resolved: {complaints.filter(c => c.status === 'RESOLVED').length}
                </button>
              </div>
            </div>
            <ComplaintTable complaints={complaints} onRefresh={fetchDashboardData} />
          </div>
        )}
      </div>
    </div>
  );
}