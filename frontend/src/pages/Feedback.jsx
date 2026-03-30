import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || window.location.origin;

export default function Feedback() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  const [rating, setRating] = useState(0);
  const [hover, setHover] = useState(0);
  const [feedbackText, setFeedbackText] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [alreadySubmitted, setAlreadySubmitted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (token) {
      axios.get(`${API_URL}/api/feedback/${token}`)
        .then(res => { if (res.data) setAlreadySubmitted(true); })
        .catch(() => {});
    }
  }, [token]);

  const handleSubmit = async () => {
    if (!rating) return setError('Please select a star rating.');
    setLoading(true);
    try {
      await axios.post(`${API_URL}/api/feedback`, {
        resolve_token: token,
        rating,
        feedback_text: feedbackText
      });
      setSubmitted(true);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to submit feedback.');
    } finally {
      setLoading(false);
    }
  };

  if (!token) return (
    <div style={styles.container}>
      <div style={styles.card}>
        <div style={{ fontSize: 60, textAlign: 'center' }}>❌</div>
        <h2 style={{ textAlign: 'center' }}>Invalid Link</h2>
      </div>
    </div>
  );

  if (alreadySubmitted) return (
    <div style={styles.container}>
      <div style={styles.card}>
        <div style={{ fontSize: 60, textAlign: 'center' }}>✅</div>
        <h2 style={{ textAlign: 'center', color: '#10b981' }}>Already Submitted</h2>
        <p style={{ textAlign: 'center', color: '#6b7280' }}>You've already submitted feedback for this complaint.</p>
      </div>
    </div>
  );

  if (submitted) return (
    <div style={styles.container}>
      <div style={styles.card}>
        <div style={{ fontSize: 70, textAlign: 'center' }}>🎉</div>
        <h2 style={{ textAlign: 'center', color: '#10b981' }}>Thank You!</h2>
        <p style={{ textAlign: 'center', color: '#6b7280' }}>Your feedback helps us improve Fixxo.</p>
      </div>
    </div>
  );

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <div style={{ fontSize: 48 }}>⭐</div>
          <h2 style={{ margin: '8px 0 4px', color: '#1f2937' }}>Rate Your Experience</h2>
          <p style={{ color: '#6b7280', fontSize: 14 }}>Complaint #{token} · Optional</p>
        </div>

        {/* Star Rating */}
        <div style={{ display: 'flex', justifyContent: 'center', gap: 8, marginBottom: 20 }}>
          {[1, 2, 3, 4, 5].map(star => (
            <span
              key={star}
              onClick={() => setRating(star)}
              onMouseEnter={() => setHover(star)}
              onMouseLeave={() => setHover(0)}
              style={{
                fontSize: 44,
                cursor: 'pointer',
                color: star <= (hover || rating) ? '#f59e0b' : '#e5e7eb',
                transition: 'color 0.15s'
              }}
            >★</span>
          ))}
        </div>

        {rating > 0 && (
          <p style={{ textAlign: 'center', color: '#6b7280', fontSize: 13, marginBottom: 16 }}>
            {['', 'Very Poor 😞', 'Poor 😕', 'OK 😐', 'Good 😊', 'Excellent! 🎉'][rating]}
          </p>
        )}

        <textarea
          value={feedbackText}
          onChange={e => setFeedbackText(e.target.value)}
          placeholder="Any comments? (optional)"
          style={{
            width: '100%', padding: '10px 14px', borderRadius: 8,
            border: '1.5px solid #e5e7eb', fontSize: 14,
            minHeight: 80, boxSizing: 'border-box', resize: 'vertical', marginBottom: 14
          }}
        />

        {error && <div style={styles.errorBox}>{error}</div>}

        <button
          onClick={handleSubmit}
          disabled={loading}
          style={{
            width: '100%', padding: '12px 0',
            background: 'linear-gradient(135deg, #667eea, #764ba2)',
            color: '#fff', border: 'none', borderRadius: 10,
            fontSize: 16, fontWeight: 700, cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading ? 0.7 : 1
          }}
        >
          {loading ? 'Submitting...' : 'Submit Feedback'}
        </button>

        <p style={{ textAlign: 'center', color: '#9ca3af', fontSize: 12, marginTop: 12 }}>
          Your feedback is anonymous and helps improve the system.
        </p>
      </div>
    </div>
  );
}

const styles = {
  container: {
    minHeight: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', padding: 16
  },
  card: {
    background: '#fff', borderRadius: 20, padding: '32px 28px',
    width: '100%', maxWidth: 420, boxShadow: '0 20px 60px rgba(0,0,0,0.15)'
  },
  errorBox: {
    background: '#fef2f2', border: '1px solid #fca5a5', color: '#dc2626',
    borderRadius: 8, padding: '10px 14px', fontSize: 13, marginBottom: 14
  }
};