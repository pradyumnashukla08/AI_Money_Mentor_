'use client';
import React, { useState } from 'react';

interface LifeEventModalProps {
  isOpen: boolean;
  onClose: () => void;
  onComplete: (eventData: any) => void;
}

export default function LifeEventModal({ isOpen, onClose, onComplete }: LifeEventModalProps) {
  const [formData, setFormData] = useState({
    monthly_income: 150000,
    monthly_expenses: 60000,
    current_savings: 500000,
    event_text: '',
  });
  
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');

    try {
      const payload = {
        profile: {
          name: "User",
          age: 30,
          monthly_income: Number(formData.monthly_income),
          monthly_expenses: Number(formData.monthly_expenses),
          current_savings: Number(formData.current_savings),
          existing_monthly_sip: 25000,
          risk_tolerance: "moderate"
        },
        event_text: formData.event_text
      };

      const res = await fetch('http://localhost:8000/strategist/life-event', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'X-API-Key': process.env.NEXT_PUBLIC_BACKEND_API_KEY || 'dev-secret-key-12345'
        },
        body: JSON.stringify(payload)
      });

      if (!res.ok) throw new Error('Failed to analyze life event.');
      
      const data = await res.json();
      onComplete(data);
    } catch (err) {
      console.error(err);
      setError('Could not connect to The Strategist Python Core.');
    } finally {
      setSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content" style={{ boxShadow: '0 0 40px rgba(163,113,247,0.15)' }}>
        {/* Header */}
        <div className="modal-header">
          <h2 className="modal-title" style={{ color: '#a371f7' }}>
            <span>💍</span> Major Life Event Modeler
          </h2>
          <button onClick={onClose} className="modal-close" style={{ color: '#8b949e' }}>×</button>
        </div>

        {/* Body */}
        <div className="modal-body">
          <p className="modal-text">
            Describe your upcoming life event (e.g., Marriage, Buying a Car, Having a Child) and verify your current balances to see how it impacts your trajectory.
          </p>

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column' }}>
            <div className="modal-input-group">
               <label className="modal-label">Event Description</label>
               <textarea 
                 name="event_text" 
                 value={formData.event_text} 
                 onChange={handleChange} 
                 placeholder="e.g., We are getting married in 6 months and need ₹10 Lakhs..."
                 style={{
                   background: 'var(--surface-base)',
                   border: '1px solid rgba(163,113,247,0.4)',
                   color: 'var(--on-surface)',
                   borderRadius: 'var(--radius-md)',
                   padding: 'var(--sp-3) var(--sp-4)',
                   outline: 'none',
                   fontFamily: 'var(--font-body)',
                   transition: 'all var(--transition-fast)',
                   width: '100%',
                   minHeight: '100px',
                   resize: 'none',
                   marginBottom: 'var(--sp-4)'
                 }}
                 required 
               />
            </div>

            <div className="modal-grid">
               <div className="modal-input-group">
                 <label className="modal-label">Monthly Income</label>
                 <input type="number" name="monthly_income" value={formData.monthly_income} onChange={handleChange} className="modal-input" required />
               </div>
               <div className="modal-input-group">
                 <label className="modal-label">Current Savings</label>
                 <input type="number" name="current_savings" value={formData.current_savings} onChange={handleChange} className="modal-input" required />
               </div>
            </div>

            {error && <p style={{ color: 'var(--error)', fontSize: '0.875rem', marginTop: 'var(--sp-2)' }}>{error}</p>}

            <button 
              type="submit" 
              disabled={submitting || !formData.event_text.trim()}
              className="modal-submit"
              style={{ background: 'linear-gradient(135deg, #8957e5, #a371f7)', color: 'white' }}
            >
              {submitting ? 'Modeling Impact...' : 'Project Event Impact'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
