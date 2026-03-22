'use client';
import React, { useState } from 'react';

interface CouplePlanModalProps {
  isOpen: boolean;
  onClose: () => void;
  onComplete: (data: any) => void;
}

export default function CouplePlanModal({ isOpen, onClose, onComplete }: CouplePlanModalProps) {
  const [formData, setFormData] = useState({
    p1_name: 'Partner 1',
    p1_income: 120000,
    p2_name: 'Partner 2',
    p2_income: 80000,
    combined_expenses: 90000,
    joint_savings: 600000,
    primary_goal: 'Buying a Home',
  });
  
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const val = e.target.type === 'number' ? Number(e.target.value) : e.target.value;
    setFormData({ ...formData, [e.target.name]: val });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');

    try {
      const res = await fetch('http://127.0.0.1:8000/analyst/couple-plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (!res.ok) throw new Error('Failed to analyze Couple Plan.');
      
      const data = await res.json();
      onComplete(data);
    } catch (err) {
      console.error(err);
      setError('Could not establish connection to The Analyst Engine.');
    } finally {
      setSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content" style={{ boxShadow: '0 0 40px rgba(192,132,252,0.15)' }}>
        {/* Header */}
        <div className="modal-header">
          <h2 className="modal-title" style={{ color: '#c084fc' }}>
            <span>👫</span> Household Equity Modeler
          </h2>
          <button onClick={onClose} className="modal-close">×</button>
        </div>

        {/* Body */}
        <div className="modal-body">
          <p className="modal-text">
            Provide the Analyst Agent with your joint financial metrics. It will calculate the optimal proportional expense split and dictate a targeted SIP plan to reach your combined goals.
          </p>

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column' }}>
            
            <div className="modal-grid">
               <div className="modal-input-group">
                 <label className="modal-label">Partner 1 Name</label>
                 <input type="text" name="p1_name" value={formData.p1_name} onChange={handleChange} className="modal-input" required />
               </div>
               <div className="modal-input-group">
                 <label className="modal-label" style={{ color: '#c084fc' }}>Partner 1 Income (₹)</label>
                 <input type="number" name="p1_income" value={formData.p1_income} onChange={handleChange} className="modal-input" style={{ borderColor: 'rgba(192,132,252,0.5)' }} required />
               </div>
            </div>

            <div className="modal-grid">
               <div className="modal-input-group">
                 <label className="modal-label">Partner 2 Name</label>
                 <input type="text" name="p2_name" value={formData.p2_name} onChange={handleChange} className="modal-input" required />
               </div>
               <div className="modal-input-group">
                 <label className="modal-label" style={{ color: '#c084fc' }}>Partner 2 Income (₹)</label>
                 <input type="number" name="p2_income" value={formData.p2_income} onChange={handleChange} className="modal-input" style={{ borderColor: 'rgba(192,132,252,0.5)' }} required />
               </div>
            </div>

            <div className="modal-grid">
               <div className="modal-input-group">
                 <label className="modal-label">Avg Combined Expenses (₹)</label>
                 <input type="number" name="combined_expenses" value={formData.combined_expenses} onChange={handleChange} className="modal-input" required />
               </div>
               <div className="modal-input-group">
                 <label className="modal-label">Joint Savings Arsenal (₹)</label>
                 <input type="number" name="joint_savings" value={formData.joint_savings} onChange={handleChange} className="modal-input" required />
               </div>
            </div>

            <div className="modal-input-group">
               <label className="modal-label">Primary Household Objective</label>
               <select name="primary_goal" value={formData.primary_goal} onChange={handleChange} className="modal-input" style={{ WebkitAppearance: 'none' }} required>
                 <option value="Buying a Home">Buying a House</option>
                 <option value="Child Education Fund">Child Education Fund</option>
                 <option value="Early Retirement (FIRE)">Joint Early Retirement (FIRE)</option>
                 <option value="Debt Liquidation">Aggressive Debt Liquidation</option>
               </select>
            </div>

            {error && <p style={{ color: 'var(--error)', fontSize: '0.875rem', marginTop: 'var(--sp-2)' }}>{error}</p>}

            <button 
              type="submit" 
              disabled={submitting}
              className="modal-submit"
              style={{ background: 'linear-gradient(135deg, #a855f7, #c084fc)', color: 'white' }}
            >
              {submitting ? 'Analyzing Joint Cashflow...' : 'Generate Proportional Split Strategy'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
