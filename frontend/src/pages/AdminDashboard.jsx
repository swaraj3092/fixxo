import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import StatsCards from '../components/StatsCards';
import StudentTable from '../components/StudentTable';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const statusColors = {
  PENDING:       { bg: '#fef3c7', color: '#92400e', label: '⏳ Pending' },
  IN_PROGRESS:   { bg: '#dbeafe', color: '#1e40af', label: '🔧 In Progress' },
  RESOLVED:      { bg: '#d1fae5', color: '#065f46', label: '✅ Resolved' },
  CANT_RESOLVE:  { bg: '#fee2e2', color: '#991b1b', label: '❌ Can\'t Resolve' },
};

const priorityColors = {
  URGENT: '#dc2626',
  HIGH:   '#ea580c',
  MEDIUM: '#f59e0b',
  LOW:    '#3b82f6',
};

function StarRating({ rating }) {
  return (
    <span>
      {[1,2,3,4,5].map(s => (
        <span key={s} style={{ color: s <= rating ? '#f59e0b' : '#d1d5db', fontSize: 16 }}>★</span>
      ))}
    </span>
  );
}

function ComplaintCard({ complaint, feedback, onRefresh }) {
  const [expanded, setExpanded] = useState(false);
  const status = statusColors[complaint.status] || statusColors.PENDING;

  return (
    <div style={{
      background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)',
      borderRadius: 12, marginBottom: 12, overflow: 'hidden'
    }}>
      {/* Row */}
      <div
        onClick={() => setExpanded(!expanded)}
        style={{ display: 'flex', alignItems: 'center', padding: '14px 16px', cursor: 'pointer', gap: 12 }}
      >
        {/* Priority dot */}
        <div style={{
          width: 10, height: 10, borderRadius: '50%', flexShrink: 0,
          background: priorityColors[complaint.priority] || '#f59e0b'
        }} />

        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
            <span style={{ color: 'white', fontWeight: 700, fontSize: 14 }}>
              {complaint.category}
            </span>
            <span style={{
              background: status.bg, color: status.color,
              padding: '2px 8px', borderRadius: 20, fontSize: 11, fontWeight: 600
            }}>
              {status.label}
            </span>
            {complaint.media_url && (
              <span style={{ background: '#312e81', color: '#a5b4fc', padding: '2px 7px', borderRadius: 20, fontSize: 11 }}>
                📷 Photo
              </span>
            )}
            {feedback && (
              <span style={{ background: '#064e3b', color: '#6ee7b7', padding: '2px 7px', borderRadius: 20, fontSize: 11 }}>
                ⭐ {feedback.rating}/5
              </span>
            )}
          </div>
          <div style={{ color: '#9ca3af', fontSize: 12, marginTop: 2 }}>
            {complaint.student_name} · {complaint.hostel_name} Rm {complaint.room_number}
          </div>
        </div>

        <div style={{ color: '#6b7280', fontSize: 12, flexShrink: 0 }}>
          #{complaint.resolve_token?.slice(0,8)}
        </div>
        <div style={{ color: '#6b7280', fontSize: 18 }}>{expanded ? '▲' : '▼'}</div>
      </div>

      {/* Expanded Detail */}
      {expanded && (
        <div style={{ borderTop: '1px solid rgba(255,255,255,0.08)', padding: '16px 20px', background: 'rgba(0,0,0,0.2)' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 12 }}>
            <Detail label="Student" value={complaint.student_name} />
            <Detail label="Phone" value={complaint.student_phone} />
            <Detail label="Hostel" value={`${complaint.hostel_name}, Room ${complaint.room_number}`} />
            <Detail label="Priority" value={complaint.priority} color={priorityColors[complaint.priority]} />
            <Detail label="Category" value={complaint.category} />
            <Detail label="Complaint ID" value={`#${complaint.resolve_token}`} />
          </div>

          {/* Message */}
          <div style={{ background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.3)', borderRadius: 8, padding: 12, marginBottom: 12 }}>
            <div style={{ color: '#a5b4fc', fontSize: 12, fontWeight: 700, marginBottom: 4 }}>💬 Complaint</div>
            <div style={{ color: '#e5e7eb', fontSize: 14 }}>{complaint.raw_message}</div>
          </div>

          {/* Can't Resolve Reason */}
          {complaint.cant_resolve_reason && (
            <div style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: 8, padding: 12, marginBottom: 12 }}>
              <div style={{ color: '#fca5a5', fontSize: 12, fontWeight: 700, marginBottom: 4 }}>⚠️ Can't Resolve Reason</div>
              <div style={{ color: '#e5e7eb', fontSize: 14 }}>{complaint.cant_resolve_reason}</div>
            </div>
          )}

          {/* Photo */}
          {complaint.media_url && (
            <div style={{ marginBottom: 12 }}>
              <div style={{ color: '#9ca3af', fontSize: 12, fontWeight: 700, marginBottom: 6 }}>📷 Attached Photo</div>
              <img
                src={complaint.media_url}
                alt="Complaint photo"
                style={{ maxWidth: '100%', maxHeight: 300, borderRadius: 8, border: '1px solid rgba(255,255,255,0.1)' }}
                onError={(e) => { e.target.style.display = 'none'; }}
              />
              <div style={{ color: '#6b7280', fontSize: 11, marginTop: 4 }}>
                Note: Image requires Twilio authentication to load
              </div>
            </div>
          )}

          {/* Feedback */}
          {feedback && (
            <div style={{ background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.3)', borderRadius: 8, padding: 12 }}>
              <div style={{ color: '#6ee7b7', fontSize: 12, fontWeight: 700, marginBottom: 6 }}>⭐ Student Feedback</div>
              <StarRating rating={feedback.rating} />
              <span style={{ color: '#9ca3af', fontSize: 12, marginLeft: 8 }}>
                {['','Very Poor','Poor','OK','Good','Excellent!'][feedback.rating]}
              </span>
              {feedback.feedback_text && (
                <div style={{ color: '#e5e7eb', fontSize: 13, marginTop: 6 }}>"{feedback.feedback_text}"</div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function Detail({ label, value, color }) {
  return (
    <div>
      <div style={{ color: '#6b7280', fontSize: 11, marginBottom: 2 }}>{label}</div>
      <div style={{ color: color || '#e5e7eb', fontSize: 13, fontWeight: 600 }}>{value || 'N/A'}</div>
    </div>
  );
}

export default function AdminDashboard() {
  const [activeTab, setActiveTab] = useState('overview');
  const [stats, setStats] = useState(null);
  const [students, setStudents] = useState([]);
  const [complaints, setComplaints] = useState([]);
  const [feedbacks, setFeedbacks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState('ALL');
  const navigate = useNavigate();

  useEffect(() => {
    const admin = localStorage.getItem('admin');
    if (!admin) { navigate('/admin/login'); return; }
    fetchDashboardData();
  }, [navigate]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [statsRes, studentsRes, complaintsRes] = await Promise.all([
        axios.get(`${API_URL}/api/admin/stats`, { withCredentials: true }),
        axios.get(`${API_URL}/api/admin/students`, { withCredentials: true }),
        axios.get(`${API_URL}/api/admin/complaints`, { withCredentials: true }),
      ]);
      setStats(statsRes.data);
      setStudents(studentsRes.data);
      setComplaints(complaintsRes.data);

      // Fetch feedback for resolved complaints
      const resolved = complaintsRes.data.filter(c => c.status === 'RESOLVED');
      const feedbackResults = await Promise.all(
        resolved.map(c =>
          axios.get(`${API_URL}/api/feedback/${c.resolve_token}`, { withCredentials: true })
            .then(r => r.data ? { token: c.resolve_token, ...r.data } : null)
            .catch(() => null)
        )
      );
      setFeedbacks(feedbackResults.filter(Boolean));
    } catch (err) {
      if (err.response?.status === 401) navigate('/admin/login');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await axios.post(`${API_URL}/api/admin/logout`, {}, { withCredentials: true });
      localStorage.removeItem('admin');
      navigate('/admin/login');
    } catch {}
  };

  const getFeedbackForComplaint = (token) => feedbacks.find(f => f.resolve_token === token);

  const filteredComplaints = filterStatus === 'ALL'
    ? complaints
    : complaints.filter(c => c.status === filterStatus);

  const avgRating = feedbacks.length
    ? (feedbacks.reduce((sum, f) => sum + f.rating, 0) / feedbacks.length).toFixed(1)
    : null;

  if (loading) return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg,#0f172a,#1e1b4b)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ textAlign: 'center' }}>
        <div style={{ fontSize: 60, animation: 'spin 1s linear infinite' }}>⚙️</div>
        <p style={{ color: 'white', fontSize: 20, marginTop: 16 }}>Loading dashboard...</p>
      </div>
    </div>
  );

  const tabs = [
    { id: 'overview',   label: '📊 Overview' },
    { id: 'complaints', label: '🎫 Complaints' },
    { id: 'feedback',   label: `⭐ Feedback${feedbacks.length ? ` (${feedbacks.length})` : ''}` },
    { id: 'students',   label: '👥 Students' },
  ];

  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg,#0f172a 0%,#1e1b4b 100%)', fontFamily: 'Arial, sans-serif' }}>

      {/* Header */}
      <header style={{ background: 'rgba(255,255,255,0.05)', backdropFilter: 'blur(10px)', borderBottom: '1px solid rgba(255,255,255,0.1)', position: 'sticky', top: 0, zIndex: 50 }}>
        <div style={{ maxWidth: 1200, margin: '0 auto', padding: '14px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <h1 style={{ color: 'white', fontSize: 24, fontWeight: 800, margin: 0 }}>🏠 Fixxo Admin</h1>
            <span style={{ background: 'rgba(167,139,250,0.2)', color: '#c4b5fd', padding: '3px 10px', borderRadius: 20, fontSize: 12, fontWeight: 600 }}>
              Live Dashboard
            </span>
          </div>
          <button onClick={handleLogout} style={{ background: 'rgba(239,68,68,0.15)', color: '#fca5a5', border: '1px solid rgba(239,68,68,0.3)', padding: '8px 16px', borderRadius: 8, cursor: 'pointer', fontWeight: 600 }}>
            🚪 Logout
          </button>
        </div>
      </header>

      {/* Tabs */}
      <div style={{ background: 'rgba(255,255,255,0.03)', borderBottom: '1px solid rgba(255,255,255,0.08)' }}>
        <div style={{ maxWidth: 1200, margin: '0 auto', padding: '0 20px', display: 'flex' }}>
          {tabs.map(tab => (
            <button key={tab.id} onClick={() => setActiveTab(tab.id)} style={{
              padding: '14px 20px', background: 'none', border: 'none', cursor: 'pointer',
              fontWeight: 700, fontSize: 14, transition: 'all 0.2s',
              color: activeTab === tab.id ? 'white' : '#6b7280',
              borderBottom: activeTab === tab.id ? '2px solid #a78bfa' : '2px solid transparent',
            }}>
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div style={{ maxWidth: 1200, margin: '0 auto', padding: '28px 20px' }}>

        {/* OVERVIEW */}
        {activeTab === 'overview' && (
          <div>
            <StatsCards stats={stats} />

            {/* Quick stats row */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px,1fr))', gap: 12, margin: '24px 0' }}>
              {[
                { label: 'Total Complaints', value: complaints.length, icon: '🎫', color: '#6366f1' },
                { label: 'Pending', value: complaints.filter(c=>c.status==='PENDING').length, icon: '⏳', color: '#f59e0b' },
                { label: 'Resolved', value: complaints.filter(c=>c.status==='RESOLVED').length, icon: '✅', color: '#10b981' },
                { label: "Can't Resolve", value: complaints.filter(c=>c.status==='CANT_RESOLVE').length, icon: '❌', color: '#ef4444' },
                { label: 'Avg Rating', value: avgRating ? `${avgRating} ★` : 'N/A', icon: '⭐', color: '#f59e0b' },
                { label: 'Feedback Count', value: feedbacks.length, icon: '💬', color: '#8b5cf6' },
              ].map(s => (
                <div key={s.label} style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 12, padding: '16px 18px' }}>
                  <div style={{ fontSize: 24 }}>{s.icon}</div>
                  <div style={{ color: s.color, fontSize: 26, fontWeight: 800, margin: '4px 0' }}>{s.value}</div>
                  <div style={{ color: '#6b7280', fontSize: 12 }}>{s.label}</div>
                </div>
              ))}
            </div>

            {/* Recent complaints */}
            <div style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 16, padding: 20 }}>
              <h2 style={{ color: 'white', fontSize: 18, fontWeight: 700, marginBottom: 16, marginTop: 0 }}>Recent Complaints</h2>
              {complaints.slice(0,5).map(c => (
                <ComplaintCard key={c.id} complaint={c} feedback={getFeedbackForComplaint(c.resolve_token)} onRefresh={fetchDashboardData} />
              ))}
            </div>
          </div>
        )}

        {/* COMPLAINTS */}
        {activeTab === 'complaints' && (
          <div>
            {/* Filter bar */}
            <div style={{ display: 'flex', gap: 8, marginBottom: 20, flexWrap: 'wrap' }}>
              {['ALL','PENDING','IN_PROGRESS','RESOLVED','CANT_RESOLVE'].map(s => (
                <button key={s} onClick={() => setFilterStatus(s)} style={{
                  padding: '7px 14px', borderRadius: 20, border: 'none', cursor: 'pointer', fontSize: 13, fontWeight: 600,
                  background: filterStatus === s ? '#6366f1' : 'rgba(255,255,255,0.08)',
                  color: filterStatus === s ? 'white' : '#9ca3af',
                }}>
                  {s === 'ALL' ? `All (${complaints.length})` : `${statusColors[s]?.label} (${complaints.filter(c=>c.status===s).length})`}
                </button>
              ))}
              <button onClick={fetchDashboardData} style={{ marginLeft: 'auto', padding: '7px 14px', borderRadius: 20, border: '1px solid rgba(255,255,255,0.15)', background: 'transparent', color: '#9ca3af', cursor: 'pointer', fontSize: 13 }}>
                🔄 Refresh
              </button>
            </div>

            {filteredComplaints.length === 0
              ? <div style={{ textAlign: 'center', color: '#6b7280', padding: 40 }}>No complaints found.</div>
              : filteredComplaints.map(c => (
                  <ComplaintCard key={c.id} complaint={c} feedback={getFeedbackForComplaint(c.resolve_token)} onRefresh={fetchDashboardData} />
                ))
            }
          </div>
        )}

        {/* FEEDBACK */}
        {activeTab === 'feedback' && (
          <div>
            {/* Summary */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(180px,1fr))', gap: 14, marginBottom: 24 }}>
              <div style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 14, padding: 20 }}>
                <div style={{ color: '#f59e0b', fontSize: 32, fontWeight: 800 }}>{avgRating || '—'}</div>
                <div style={{ color: 'white', fontWeight: 700 }}>Average Rating</div>
                {avgRating && <div style={{ marginTop: 4 }}><StarRating rating={Math.round(avgRating)} /></div>}
              </div>
              <div style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 14, padding: 20 }}>
                <div style={{ color: '#10b981', fontSize: 32, fontWeight: 800 }}>{feedbacks.length}</div>
                <div style={{ color: 'white', fontWeight: 700 }}>Total Feedbacks</div>
                <div style={{ color: '#6b7280', fontSize: 12, marginTop: 2 }}>
                  {complaints.filter(c=>c.status==='RESOLVED').length} resolved complaints
                </div>
              </div>
              {[5,4,3,2,1].map(star => {
                const count = feedbacks.filter(f=>f.rating===star).length;
                const pct = feedbacks.length ? Math.round(count/feedbacks.length*100) : 0;
                return (
                  <div key={star} style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 10, padding: '12px 16px', display: 'flex', alignItems: 'center', gap: 10 }}>
                    <span style={{ color: '#f59e0b', fontSize: 18 }}>{'★'.repeat(star)}</span>
                    <div style={{ flex: 1 }}>
                      <div style={{ background: 'rgba(255,255,255,0.1)', borderRadius: 4, height: 6 }}>
                        <div style={{ background: '#f59e0b', width: `${pct}%`, height: '100%', borderRadius: 4 }} />
                      </div>
                    </div>
                    <span style={{ color: '#9ca3af', fontSize: 12 }}>{count}</span>
                  </div>
                );
              })}
            </div>

            {/* Feedback cards */}
            {feedbacks.length === 0
              ? <div style={{ textAlign: 'center', color: '#6b7280', padding: 60, background: 'rgba(255,255,255,0.03)', borderRadius: 16, border: '1px solid rgba(255,255,255,0.08)' }}>
                  <div style={{ fontSize: 48, marginBottom: 12 }}>⭐</div>
                  <div>No feedback submitted yet.</div>
                  <div style={{ fontSize: 12, marginTop: 4 }}>Feedbacks appear after students rate resolved complaints.</div>
                </div>
              : feedbacks.map(fb => {
                  const complaint = complaints.find(c => c.resolve_token === fb.resolve_token);
                  return (
                    <div key={fb.id} style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 12, padding: '16px 20px', marginBottom: 10 }}>
                      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap' }}>
                        <div>
                          <StarRating rating={fb.rating} />
                          <span style={{ color: '#9ca3af', fontSize: 12, marginLeft: 8 }}>
                            {['','Very Poor','Poor','OK','Good','Excellent!'][fb.rating]}
                          </span>
                          {fb.feedback_text && (
                            <div style={{ color: '#e5e7eb', fontSize: 14, marginTop: 8, fontStyle: 'italic' }}>
                              "{fb.feedback_text}"
                            </div>
                          )}
                          {complaint && (
                            <div style={{ color: '#6b7280', fontSize: 12, marginTop: 6 }}>
                              {complaint.category} · {complaint.hostel_name} Rm {complaint.room_number} · {complaint.student_name}
                            </div>
                          )}
                        </div>
                        <span style={{ background: 'rgba(16,185,129,0.1)', color: '#6ee7b7', padding: '3px 10px', borderRadius: 20, fontSize: 11, fontWeight: 600, flexShrink: 0 }}>
                          #{fb.resolve_token?.slice(0,8)}
                        </span>
                      </div>
                    </div>
                  );
                })
            }
          </div>
        )}

        {/* STUDENTS */}
        {activeTab === 'students' && (
          <div style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 16, padding: 20 }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
              <h2 style={{ color: 'white', fontSize: 20, fontWeight: 700, margin: 0 }}>Registered Students</h2>
              <span style={{ color: '#9ca3af', fontSize: 14 }}>Total: <strong style={{ color: 'white' }}>{students.length}</strong></span>
            </div>
            <StudentTable students={students} onRefresh={fetchDashboardData} />
          </div>
        )}
      </div>
    </div>
  );
}