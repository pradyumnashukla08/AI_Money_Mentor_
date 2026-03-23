'use client';
import React, { useState, useEffect } from 'react';

interface Question {
  id: string;
  text: string;
  dimension: string;
  options: string[];
}

interface HealthScoreModalProps {
  isOpen: boolean;
  onClose: () => void;
  onComplete: (scoreData: any) => void;
}

export default function HealthScoreModal({ isOpen, onClose, onComplete }: HealthScoreModalProps) {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  // Fetch Questions from Python Background Server
  useEffect(() => {
    if (isOpen) {
      setLoading(true);
      fetch('http://127.0.0.1:8000/api/health-score/questions', {
        headers: { 'X-API-Key': process.env.NEXT_PUBLIC_BACKEND_API_KEY || 'dev-secret-key-12345' }
      })
        .then(res => res.json())
        .then(data => {
          setQuestions(data.questions || []);
          setLoading(false);
        })
        .catch(err => {
          console.error(err);
          setError('Could not connect to the Python AI core. Is uvicorn running?');
          setLoading(false);
        });
    }
  }, [isOpen]);

  const handleOptionSelect = (optionIndex: number) => {
    const activeQuestion = questions[currentIndex];
    setAnswers(prev => ({ ...prev, [activeQuestion.id]: optionIndex }));
    
    // Auto-advance
    if (currentIndex < questions.length - 1) {
      setTimeout(() => setCurrentIndex(c => c + 1), 300);
    }
  };

  const submitQuiz = async () => {
    setSubmitting(true);
    try {
      const payload = {
        answers,
        name: "User",
        age: 30,
        monthly_income: 150000,
      };
      
      const res = await fetch('http://127.0.0.1:8000/api/health-score/calculate', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'X-API-Key': process.env.NEXT_PUBLIC_BACKEND_API_KEY || 'dev-secret-key-12345'
        },
        body: JSON.stringify(payload)
      });
      
      if (!res.ok) throw new Error('Calculation failed');
      const data = await res.json();
      onComplete(data.health_score);
    } catch (err) {
      console.error(err);
      setError("Failed to calculate the Health Score visually.");
    } finally {
      setSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content" style={{ boxShadow: '0 0 40px rgba(240,185,11,0.15)', maxHeight: '90vh' }}>
        {/* Header */}
        <div className="modal-header">
          <div>
            <h2 className="modal-title">
              <span>💪</span> Money Health Score Quiz
            </h2>
            {questions.length > 0 && !submitting && (
              <p style={{ fontSize: '0.875rem', color: 'var(--on-surface-variant)', marginTop: '4px' }}>Question {currentIndex + 1} of {questions.length}</p>
            )}
          </div>
          <button onClick={onClose} className="modal-close">×</button>
        </div>

        {/* Body */}
        <div className="modal-body" style={{ display: 'flex', flexDirection: 'column' }}>
          {loading ? (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '3rem', color: 'var(--on-surface-variant)' }}>
              <div style={{ animation: 'pulse-dot 1.5s infinite', width: '30px', height: '30px', background: 'var(--primary)', borderRadius: '50%', marginBottom: '1rem' }} />
              <p>Fetching AI Quiz parameters...</p>
            </div>
          ) : error ? (
            <div style={{ color: 'var(--error)', padding: '1rem', background: 'rgba(147,0,10,0.2)', borderRadius: 'var(--radius-xl)', border: '1px solid var(--error-container)' }}>
              {error}
            </div>
          ) : submitting ? (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '3rem', color: 'var(--on-surface-variant)' }}>
              <div style={{ animation: 'pulse-dot 1s infinite', width: '30px', height: '30px', background: 'var(--primary)', borderRadius: '50%', marginBottom: '1rem' }} />
              <p>The Tax Auditor is parsing your metrics...</p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--sp-6)' }}>
              <div className="quiz-progress-bar">
                <div 
                  className="quiz-progress-fill"
                  style={{ width: `${((currentIndex) / questions.length) * 100}%` }}
                />
              </div>

              <div style={{ background: 'var(--surface-base)', border: '1px solid var(--surface-highest)', borderRadius: 'var(--radius-xl)', padding: 'var(--sp-6)' }}>
                <h3 className="modal-label" style={{ marginBottom: 'var(--sp-2)' }}>
                  {questions[currentIndex]?.dimension}
                </h3>
                <p style={{ fontSize: '1.125rem', color: 'var(--on-surface)', fontWeight: 500, lineHeight: 1.6, marginBottom: 'var(--sp-6)' }}>
                  {questions[currentIndex]?.text}
                </p>

                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--sp-3)' }}>
                  {questions[currentIndex]?.options.map((option, idx) => {
                    const isSelected = answers[questions[currentIndex].id] === idx;
                    return (
                      <button
                        key={idx}
                        onClick={() => handleOptionSelect(idx)}
                        className={`quiz-option ${isSelected ? 'selected' : ''}`}
                      >
                        {option}
                      </button>
                    )
                  })}
                </div>
              </div>

              {/* Navigation */}
              <div className="quiz-nav">
                <button 
                  onClick={() => setCurrentIndex(c => Math.max(0, c - 1))}
                  disabled={currentIndex === 0}
                  className="quiz-btn"
                >
                  ← Back
                </button>

                {currentIndex === questions.length - 1 && answers[questions[currentIndex]?.id] !== undefined ? (
                  <button 
                    onClick={submitQuiz}
                    className="modal-submit"
                    style={{ marginTop: 0, width: 'auto' }}
                  >
                    Submit Quiz & Calculate →
                  </button>
                ) : (
                  <button 
                    onClick={() => setCurrentIndex(c => Math.min(questions.length - 1, c + 1))}
                    disabled={answers[questions[currentIndex]?.id] === undefined}
                    className="quiz-btn primary"
                  >
                    Next →
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
