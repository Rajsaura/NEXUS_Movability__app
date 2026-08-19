import React from 'react';
import { Bike, Train, Bus, AlertCircle } from 'lucide-react';

interface TransportOption {
  mode: string;
  is_supported: boolean;
  unsupported_reason?: string;
  total_distance_km: number;
  total_time_minutes: number;
  total_cost_inr: number;
  estimated_co2_kg: number;
  convenience_score: number;
  overall_score: number;
  provenance: {
    distance: { source_type: string; confidence: string };
    duration: { source_type: string; confidence: string };
    fare: { source_type: string; confidence: string };
    co2: { source_type: string; confidence: string; ui_co2_label?: string };
    ui_co2_label?: string;
  };
  assumptions: string[];
  details?: any;
}

interface ComparisonCardsProps {
  options: TransportOption[];
  recommendedMode: string;
}

export const ComparisonCards: React.FC<ComparisonCardsProps> = ({ options, recommendedMode }) => {
  return (
    <div className="modes-grid">
      {options.map((opt) => {
        const isWinner = opt.mode === recommendedMode;
        
        if (!opt.is_supported) {
          return (
            <div key={opt.mode} className="mode-card unsupported">
              <div className="mode-header">
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Bus size={20} color="var(--text-muted)" />
                  <h3 style={{ fontSize: '1.1rem' }}>MTC Bus</h3>
                </div>
                <span className="badge-tag badge-unsupported">UNSUPPORTED</span>
              </div>
              <div style={{ fontSize: '0.85rem', color: 'var(--accent-rose)', margin: '1rem 0' }}>
                <AlertCircle size={16} style={{ display: 'inline', marginRight: '4px', verticalAlign: 'middle' }} />
                {opt.unsupported_reason || 'Bus comparison is currently available only for supported Chennai corridors.'}
              </div>
            </div>
          );
        }

        return (
          <div key={opt.mode} className={`mode-card ${isWinner ? 'winner' : ''}`}>
            <div className="mode-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                {opt.mode === 'BIKE' && <Bike size={20} color="var(--accent-cyan)" />}
                {opt.mode === 'METRO' && <Train size={20} color="var(--accent-emerald)" />}
                {opt.mode === 'MTC_BUS' && <Bus size={20} color="var(--accent-amber)" />}
                <h3 style={{ fontSize: '1.1rem' }}>
                  {opt.mode === 'BIKE' && 'Private Bike'}
                  {opt.mode === 'METRO' && 'Chennai Metro'}
                  {opt.mode === 'MTC_BUS' && 'MTC Bus Corridor'}
                </h3>
              </div>
              {isWinner ? (
                <span className="badge-tag badge-high">RECOMMENDED</span>
              ) : (
                <span className="badge-tag badge-medium">SCORE: {opt.overall_score}</span>
              )}
            </div>

            <div className="metric-row">
              <span style={{ color: 'var(--text-muted)' }}>Distance</span>
              <span><strong>{opt.total_distance_km.toFixed(1)} km</strong></span>
            </div>

            <div className="metric-row">
              <span style={{ color: 'var(--text-muted)' }}>Travel Time</span>
              <span><strong>{opt.total_time_minutes} mins</strong></span>
            </div>

            <div className="metric-row">
              <span style={{ color: 'var(--text-muted)' }}>Cost (INR)</span>
              <span><strong>₹{opt.total_cost_inr.toFixed(0)}</strong></span>
            </div>

            <div className="metric-row">
              <span style={{ color: 'var(--text-muted)' }}>Estimated CO2</span>
              <span style={{ color: 'var(--accent-green)' }}><strong>{opt.estimated_co2_kg.toFixed(2)} kg</strong></span>
            </div>

            <div className="metric-row">
              <span style={{ color: 'var(--text-muted)' }}>Convenience Score</span>
              <span><strong>{opt.convenience_score}/100</strong></span>
            </div>

            {opt.details && opt.mode === 'METRO' && (
              <div style={{ marginTop: '0.75rem', fontSize: '0.78rem', color: 'var(--text-muted)', background: 'rgba(15, 23, 42, 0.4)', padding: '0.5rem', borderRadius: '0.375rem' }}>
                <div><strong>Route:</strong> {opt.details.source_station} → {opt.details.dest_station}</div>
                {opt.details.interchange && <div><strong>Interchange:</strong> {opt.details.interchange}</div>}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};
