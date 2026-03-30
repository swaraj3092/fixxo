import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || window.location.origin;

const inputStyle = {
  width: '100%',
  padding: '12px',
  border: '2px solid #d1d5db',
  borderRadius: '8px',
  fontSize: '16px',
  boxSizing: 'border-box'
};

const labelStyle = {
  display: 'block',
  fontWeight: 'bold',
  marginBottom: '8px',
  color: '#374151'
};

export default function Register() {
  const [formData, setFormData] = useState({
    phone_number: '',
    roll_number: '',
    student_name: '',
    hostel_name: '',
    room_number: '',
    email: ''
  });

  // Hostel toggle state
  const [hostelType, setHostelType] = useState('KP'); // 'KP' or 'QC'
  const [hostelNumber, setHostelNumber] = useState('');

  // OTP flow state
  const [otpSent, setOtpSent] = useState(false);
  const [otpVerified, setOtpVerified] = useState(false);
  const [otp, setOtp] = useState('');
  const [otpLoading, setOtpLoading] = useState(false);
  const [otpError, setOtpError] = useState('');
  const [otpSuccess, setOtpSuccess] = useState('');
  const [countdown, setCountdown] = useState(0);

  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  // Parse phone from URL
  useEffect(() => {
    try {
      const params = new URLSearchParams(window.location.search);
      const phone = params.get('phone');
      if (phone) {
        let formattedPhone = phone;
        if (!formattedPhone.startsWith('whatsapp:')) {
          if (!formattedPhone.startsWith('+')) formattedPhone = `+${formattedPhone}`;
          formattedPhone = `whatsapp:${formattedPhone}`;
        }
        setFormData(prev => ({ ...prev, phone_number: formattedPhone }));
      }
    } catch (err) {
      console.error('Error parsing URL:', err);
    }
  }, []);

  // Countdown timer for OTP resend
  useEffect(() => {
    if (countdown <= 0) return;
    const timer = setTimeout(() => setCountdown(c => c - 1), 1000);
    return () => clearTimeout(timer);
  }, [countdown]);

  // Update hostel_name whenever hostelType or hostelNumber changes
  useEffect(() => {
    if (hostelNumber) {
      setFormData(prev => ({ ...prev, hostel_name: `${hostelType}-${hostelNumber}` }));
    } else {
      setFormData(prev => ({ ...prev, hostel_name: '' }));
    }
  }, [hostelType, hostelNumber]);

  // Email validation
  const isValidKiitEmail = (email) => {
    return email.trim().toLowerCase().endsWith('@kiit.ac.in');
  };

  const handleSendOtp = async () => {
    setOtpError('');
    setOtpSuccess('');

    if (!formData.email) {
      setOtpError('Please enter your KIIT email first.');
      return;
    }
    if (!isValidKiitEmail(formData.email)) {
      setOtpError('Only @kiit.ac.in email addresses are allowed.');
      return;
    }

    setOtpLoading(true);
    try {
      await axios.post(`${API_URL}/api/send-otp`, { email: formData.email });
      setOtpSent(true);
      setCountdown(60);
      setOtpSuccess(`OTP sent to ${formData.email}! Check your inbox.`);
    } catch (err) {
      setOtpError(err.response?.data?.error || 'Failed to send OTP. Try again.');
    } finally {
      setOtpLoading(false);
    }
  };

  const handleVerifyOtp = async () => {
    setOtpError('');
    if (!otp || otp.length !== 6) {
      setOtpError('Please enter the 6-digit OTP.');
      return;
    }
    setOtpLoading(true);
    try {
      await axios.post(`${API_URL}/api/verify-otp`, { email: formData.email, otp });
      setOtpVerified(true);
      setOtpSuccess('✅ Email verified successfully!');
    } catch (err) {
      setOtpError(err.response?.data?.error || 'Invalid or expired OTP.');
    } finally {
      setOtpLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!formData.phone_number) {
      setError('Phone number is missing. Please use the registration link from WhatsApp.');
      return;
    }
    if (!isValidKiitEmail(formData.email)) {
      setError('Only @kiit.ac.in email addresses are allowed.');
      return;
    }
    if (!otpVerified) {
      setError('Please verify your email with OTP before registering.');
      return;
    }
    if (!hostelNumber) {
      setError('Please enter your hostel number.');
      return;
    }

    setLoading(true);
    const submitData = { ...formData, college_id: `FIXXO${Date.now()}` };

    try {
      await axios.post(`${API_URL}/api/register`, submitData);
      setSuccess(true);
    } catch (err) {
      setError(err.response?.data?.error || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px'
      }}>
        <div style={{
          backgroundColor: 'white', borderRadius: '20px', padding: '40px',
          maxWidth: '500px', width: '100%', textAlign: 'center',
          boxShadow: '0 20px 60px rgba(0,0,0,0.3)'
        }}>
          <div style={{ fontSize: '80px', marginBottom: '20px' }}>✅</div>
          <h1 style={{ fontSize: '32px', color: '#1f2937', marginBottom: '20px' }}>Registration Complete!</h1>
          <p style={{ fontSize: '18px', color: '#6b7280', marginBottom: '30px' }}>
            You can now send complaints via WhatsApp. We'll automatically use your registered details.
          </p>
          <div style={{
            backgroundColor: '#eff6ff', border: '2px solid #3b82f6',
            borderRadius: '10px', padding: '20px'
          }}>
            <p style={{ fontSize: '14px', color: '#1e40af', fontWeight: 'bold', marginBottom: '10px' }}>
              Send your complaint to:
            </p>
            <p style={{ fontSize: '24px', color: '#2563eb', fontFamily: 'monospace' }}>+1 415 523 8886</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px'
    }}>
      <div style={{
        backgroundColor: 'white', borderRadius: '20px', padding: '40px',
        maxWidth: '600px', width: '100%', boxShadow: '0 20px 60px rgba(0,0,0,0.3)'
      }}>
        <div style={{ textAlign: 'center', marginBottom: '30px' }}>
          <h1 style={{ fontSize: '36px', color: '#1f2937', marginBottom: '10px' }}>🏠 Fixxo Registration</h1>
          <p style={{ color: '#6b7280' }}>One-time setup for hostel complaint tracking</p>
        </div>

        <form onSubmit={handleSubmit}>

          {/* Roll Number */}
          <div style={{ marginBottom: '20px' }}>
            <label style={labelStyle}>Roll Number *</label>
            <input
              type="text" required value={formData.roll_number}
              onChange={(e) => setFormData({ ...formData, roll_number: e.target.value })}
              style={inputStyle} placeholder="e.g., 2305XXXX"
            />
          </div>

          {/* Full Name */}
          <div style={{ marginBottom: '20px' }}>
            <label style={labelStyle}>Full Name *</label>
            <input
              type="text" required value={formData.student_name}
              onChange={(e) => setFormData({ ...formData, student_name: e.target.value })}
              style={inputStyle} placeholder="e.g., Swaraj Kumar Behera"
            />
          </div>

          {/* KIIT Email + OTP */}
          <div style={{ marginBottom: '20px' }}>
            <label style={labelStyle}>KIIT Email *</label>
            <div style={{ display: 'flex', gap: '10px' }}>
              <input
                type="email" required value={formData.email}
                onChange={(e) => {
                  setFormData({ ...formData, email: e.target.value });
                  setOtpVerified(false);
                  setOtpSent(false);
                  setOtpSuccess('');
                  setOtpError('');
                  setOtp('');
                }}
                style={{
                  ...inputStyle,
                  flex: 1,
                  borderColor: otpVerified ? '#10b981' : formData.email && !isValidKiitEmail(formData.email) ? '#ef4444' : '#d1d5db'
                }}
                placeholder="yourname@kiit.ac.in"
                disabled={otpVerified}
              />
              {!otpVerified && (
                <button
                  type="button"
                  onClick={handleSendOtp}
                  disabled={otpLoading || countdown > 0 || !formData.email}
                  style={{
                    padding: '12px 16px',
                    background: countdown > 0 ? '#9ca3af' : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    color: 'white', border: 'none', borderRadius: '8px',
                    fontWeight: 'bold', cursor: countdown > 0 ? 'not-allowed' : 'pointer',
                    whiteSpace: 'nowrap', fontSize: '14px'
                  }}
                >
                  {otpLoading ? 'Sending...' : countdown > 0 ? `Resend (${countdown}s)` : otpSent ? 'Resend OTP' : 'Send OTP'}
                </button>
              )}
            </div>

            {/* Email domain hint */}
            {formData.email && !isValidKiitEmail(formData.email) && (
              <p style={{ fontSize: '12px', color: '#ef4444', marginTop: '5px' }}>
                ⚠️ Only @kiit.ac.in emails are allowed.
              </p>
            )}

            {/* OTP Input */}
            {otpSent && !otpVerified && (
              <div style={{ marginTop: '12px' }}>
                <div style={{ display: 'flex', gap: '10px' }}>
                  <input
                    type="text" maxLength={6} value={otp}
                    onChange={(e) => setOtp(e.target.value.replace(/\D/g, ''))}
                    style={{ ...inputStyle, flex: 1, letterSpacing: '6px', fontWeight: 'bold', fontSize: '20px', textAlign: 'center' }}
                    placeholder="------"
                  />
                  <button
                    type="button" onClick={handleVerifyOtp}
                    disabled={otpLoading || otp.length !== 6}
                    style={{
                      padding: '12px 16px',
                      background: otp.length !== 6 ? '#9ca3af' : 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                      color: 'white', border: 'none', borderRadius: '8px',
                      fontWeight: 'bold', cursor: otp.length !== 6 ? 'not-allowed' : 'pointer',
                      fontSize: '14px'
                    }}
                  >
                    {otpLoading ? 'Verifying...' : 'Verify OTP'}
                  </button>
                </div>
              </div>
            )}

            {otpSuccess && (
              <p style={{ fontSize: '13px', color: '#10b981', marginTop: '6px', fontWeight: 'bold' }}>
                {otpSuccess}
              </p>
            )}
            {otpError && (
              <p style={{ fontSize: '13px', color: '#ef4444', marginTop: '6px' }}>
                ❌ {otpError}
              </p>
            )}
          </div>

          {/* Hostel Type Toggle + Number */}
          <div style={{ marginBottom: '20px' }}>
            <label style={labelStyle}>Hostel *</label>

            {/* KP / QC Toggle */}
            <div style={{
              display: 'inline-flex', backgroundColor: '#f3f4f6',
              borderRadius: '10px', padding: '4px', marginBottom: '12px'
            }}>
              {['KP', 'QC'].map(type => (
                <button
                  key={type} type="button"
                  onClick={() => { setHostelType(type); setHostelNumber(''); }}
                  style={{
                    padding: '8px 28px', borderRadius: '8px', border: 'none',
                    fontWeight: 'bold', fontSize: '16px', cursor: 'pointer',
                    background: hostelType === type
                      ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                      : 'transparent',
                    color: hostelType === type ? 'white' : '#6b7280',
                    transition: 'all 0.2s'
                  }}
                >
                  {type}
                </button>
              ))}
            </div>

            {/* Hostel Number */}
            <input
              type="number" required min="1" max="30"
              value={hostelNumber}
              onChange={(e) => setHostelNumber(e.target.value)}
              style={inputStyle}
              placeholder={`Enter ${hostelType} number (e.g., 7 → ${hostelType}-7)`}
            />
            {hostelNumber && (
              <p style={{ fontSize: '13px', color: '#667eea', marginTop: '5px', fontWeight: 'bold' }}>
                📍 Hostel: {hostelType}-{hostelNumber}
              </p>
            )}
          </div>

          {/* Room Number */}
          <div style={{ marginBottom: '20px' }}>
            <label style={labelStyle}>Room Number *</label>
            <input
              type="text" required value={formData.room_number}
              onChange={(e) => setFormData({ ...formData, room_number: e.target.value })}
              style={inputStyle} placeholder="e.g., 305"
            />
          </div>

          {/* WhatsApp Number (Read-only) */}
          <div style={{ marginBottom: '20px' }}>
            <label style={labelStyle}>WhatsApp Number</label>
            <input
              type="text"
              value={formData.phone_number || 'Not provided — use the link from WhatsApp'}
              disabled
              style={{ ...inputStyle, backgroundColor: '#f3f4f6', color: '#6b7280' }}
            />
            {!formData.phone_number && (
              <p style={{ fontSize: '12px', color: '#dc2626', marginTop: '5px' }}>
                ⚠️ Use the registration link sent to you on WhatsApp.
              </p>
            )}
          </div>

          {/* Error */}
          {error && (
            <div style={{
              backgroundColor: '#fee2e2', border: '2px solid #ef4444',
              borderRadius: '8px', padding: '15px', marginBottom: '20px', color: '#991b1b'
            }}>
              ❌ {error}
            </div>
          )}

          {/* Submit */}
          <button
            type="submit"
            disabled={loading || !formData.phone_number || !otpVerified}
            style={{
              width: '100%',
              background: loading || !formData.phone_number || !otpVerified
                ? 'linear-gradient(135deg, #9ca3af 0%, #6b7280 100%)'
                : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white', fontWeight: 'bold', padding: '15px',
              borderRadius: '8px', border: 'none', fontSize: '18px',
              cursor: loading || !formData.phone_number || !otpVerified ? 'not-allowed' : 'pointer',
              opacity: loading || !formData.phone_number || !otpVerified ? 0.7 : 1
            }}
          >
            {loading ? 'Registering...' : !otpVerified ? '🔒 Verify Email to Register' : '✅ Complete Registration'}
          </button>
        </form>
      </div>
    </div>
  );
}