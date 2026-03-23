'use client';
import React, { useState } from 'react';

interface FirePlanModalProps {
  isOpen: boolean;
  onClose: () => void;
  onComplete: (fireData: any) => void;
}

export default function FirePlanModal({ isOpen, onClose, onComplete }: FirePlanModalProps) {
  const [formData, setFormData] = useState({
    age: 30,
    monthly_income: 100000,
    monthly_expenses: 40000,
    current_savings: 500000,
    existing_monthly_sip: 20000,
    target_retirement_age: 50,
  });
  
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: Number(e.target.value) });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');

    try {
      const payload = {
        profile: {
          name: "User",
          age: formData.age,
          monthly_income: formData.monthly_income,
          monthly_expenses: formData.monthly_expenses,
          current_savings: formData.current_savings,
          existing_monthly_sip: formData.existing_monthly_sip,
          risk_tolerance: "aggressive"
        },
        goal: {
          target_retirement_age: formData.target_retirement_age,
          desired_monthly_expense: formData.monthly_expenses * 1.5, // Inflation buffer
          withdrawal_rate: 0.04
        }
      };

      const res = await fetch('http://localhost:8000/strategist/fire-plan', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'X-API-Key': process.env.NEXT_PUBLIC_BACKEND_API_KEY || 'dev-secret-key-12345'
        },
        body: JSON.stringify(payload)
      });

      if (!res.ok) throw new Error('Failed to generate FIRE protocol');
      
      const data = await res.json();
      onComplete(data);
    } catch (err) {
      console.error(err);
      setError('Could not establish connection to The Strategist Python engine.');
    } finally {
      setSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        {/* Header */}
        <div className="modal-header">
          <h2 className="modal-title">
            <span>🔥</span> F.I.R.E. Architect
          </h2>
          <button onClick={onClose} className="modal-close">×</button>
        </div>

        {/* Body */}
        <div className="modal-body">
          <p className="modal-text">
            The Strategist requires your precise economic metrics to calculate your Financial Independence, Retire Early (FIRE) roadmap matrix.
          </p>

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column' }}>
            <div className="modal-grid">
               <div className="modal-input-group">
                 <label className="modal-label">Current Age</label>
                 <input type="number" name="age" value={formData.age} onChange={handleChange} className="modal-input" required />
               </div>
               <div className="modal-input-group">
                 <label className="modal-label" style={{ color: 'var(--primary)' }}>Target Retire Age</label>
                 <input type="number" name="target_retirement_age" value={formData.target_retirement_age} onChange={handleChange} className="modal-input" style={{ borderColor: 'var(--primary)', color: 'var(--primary)', fontWeight: 'bold' }} required />
               </div>
            </div>

            <div className="modal-grid">
               <div className="modal-input-group">
                 <label className="modal-label">Monthly Income (₹)</label>
                 <input type="number" name="monthly_income" value={formData.monthly_income} onChange={handleChange} className="modal-input" required />
               </div>
               <div className="modal-input-group">
                 <label className="modal-label">Monthly Expense (₹)</label>
                 <input type="number" name="monthly_expenses" value={formData.monthly_expenses} onChange={handleChange} className="modal-input" required />
               </div>
            </div>

            <div className="modal-grid">
               <div className="modal-input-group">
                 <label className="modal-label">Current Savings (₹)</label>
                 <input type="number" name="current_savings" value={formData.current_savings} onChange={handleChange} className="modal-input" required />
               </div>
               <div className="modal-input-group">
                 <label className="modal-label">Current SIP (₹)</label>
                 <input type="number" name="existing_monthly_sip" value={formData.existing_monthly_sip} onChange={handleChange} className="modal-input" required />
               </div>
            </div>

            {error && <p style={{ color: 'var(--error)', fontSize: '0.875rem', marginTop: 'var(--sp-2)' }}>{error}</p>}

            <button 
              type="submit" 
              disabled={submitting}
              className="modal-submit"
            >
              {submitting ? 'Calculating Paradigm...' : 'Generate F.I.R.E. Roadmap'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
