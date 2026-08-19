import React from 'react';
import { Award, Clock, IndianRupee, Leaf } from 'lucide-react';

interface RecommendedOption {
  mode: string;
  overall_score: number;
  total_time_minutes: number;
  total_cost_inr: number;
  estimated_co2_kg: number;
  why_recommended: string[];
}

interface RecommendationCardProps {
  recommendation: RecommendedOption;
  priority: string;
}

export const RecommendationCard: React.FC<RecommendationCardProps> = ({ recommendation, priority }) => {
  return (
    <div className="recommendation-card">
      <div className="score-badge">
        Score: {recommendation.overall_score}/100
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--accent-emerald)', marginBottom: '0.5rem' }}>
        <Award size={20} />
        <span style={{ fontSize: '0.85rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          SMART CHOICE RECOMMENDATION ({priority.replace('_', ' ').toUpperCase()})
        </span>
      </div>

      <h2 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: '1rem', color: '#ffffff' }}>
        {recommendation.mode === 'BIKE' && 'Private Bike / Scooter'}
        {recommendation.mode === 'METRO' && 'Chennai Metro (CMRL)'}
        {recommendation.mode === 'MTC_BUS' && 'MTC City Bus'}
      </h2>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginBottom: '1.25rem' }}>
        <div style={{ background: 'rgba(15, 23, 42, 0.4)', padding: '0.75rem', borderRadius: '0.5rem' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <Clock size={12} /> Travel Time
          </div>
          <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#ffffff' }}>
            {recommendation.total_time_minutes} min
          </div>
        </div>

        <div style={{ background: 'rgba(15, 23, 42, 0.4)', padding: '0.75rem', borderRadius: '0.5rem' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <IndianRupee size={12} /> Travel Cost
          </div>
          <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#ffffff' }}>
            ₹{recommendation.total_cost_inr.toFixed(0)}
          </div>
        </div>

        <div style={{ background: 'rgba(15, 23, 42, 0.4)', padding: '0.75rem', borderRadius: '0.5rem' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <Leaf size={12} /> Estimated CO2
          </div>
          <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--accent-green)' }}>
            {recommendation.estimated_co2_kg.toFixed(2)} kg
          </div>
        </div>
      </div>

      <h4 style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>Why Recommended?</h4>
      <ul className="why-bullets">
        {recommendation.why_recommended.map((bullet, idx) => (
          <li key={idx}>{bullet}</li>
        ))}
      </ul>
    </div>
  );
};
