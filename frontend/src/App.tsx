import React, { useState, useEffect } from 'react';
import { SearchForm } from './components/SearchForm';
import { RecommendationCard } from './components/RecommendationCard';
import { ComparisonCards } from './components/ComparisonCards';
import { ProvenancesDrawer } from './components/ProvenancesDrawer';
import { RouteMap } from './components/RouteMap';
import { Zap, MapPin } from 'lucide-react';

export default function App() {
  const [petrolPrice, setPetrolPrice] = useState(100.75);
  const [commuteData, setCommuteData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchCommuteData = async (params: {
    originText: string;
    destinationText: string;
    priority: string;
    bikeMileage: number;
  }) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('/api/commute/compare', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          origin: { text: params.originText },
          destination: { text: params.destinationText },
          priority: params.priority,
          bike_mileage_kmpl: params.bikeMileage
        })
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Failed to compare commute options.');
      }

      const data = await res.json();
      setCommuteData(data);
    } catch (err: any) {
      setError(err.message || 'An error occurred while computing routes.');
    } finally {
      setLoading(false);
    }
  };

  // Initial demo load
  useEffect(() => {
    fetchCommuteData({
      originText: 'VIT Chennai',
      destinationText: 'Chennai Central',
      priority: 'best_overall',
      bikeMileage: 45.0
    });
  }, []);

  return (
    <div className="container">
      <header>
        <div className="logo-tag">
          <Zap size={14} /> SMART COMMUTE CHENNAI MVP
        </div>
        <h1 className="main-title">Smart Commute Chennai</h1>
        <p className="tagline">"Choose the smartest way to travel."</p>
      </header>

      <SearchForm
        onSearch={fetchCommuteData}
        petrolPrice={petrolPrice}
        onUpdatePetrolPrice={setPetrolPrice}
        loading={loading}
      />

      {error && (
        <div style={{ background: 'rgba(244, 63, 94, 0.15)', border: '1px solid rgba(244, 63, 94, 0.4)', color: '#f43f5e', padding: '1rem', borderRadius: '0.75rem', marginTop: '1.5rem', textAlign: 'center' }}>
          {error}
        </div>
      )}

      {commuteData && (
        <>
          <div className="grid-two">
            <RecommendationCard
              recommendation={commuteData.recommended_option}
              priority={commuteData.query.priority}
            />

            <div className="glass-card" style={{ padding: '1rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem', color: 'var(--accent-cyan)', fontSize: '0.9rem', fontWeight: 600 }}>
                <MapPin size={16} /> Interactive Journey Route Map
              </div>
              <RouteMap
                origin={commuteData.query.origin}
                destination={commuteData.query.destination}
              />
            </div>
          </div>

          <h3 style={{ fontSize: '1.25rem', marginTop: '2.5rem', color: '#ffffff', borderBottom: '1px solid rgba(255, 255, 255, 0.1)', paddingBottom: '0.5rem' }}>
            Transport Modes Breakdown
          </h3>

          <ComparisonCards
            options={commuteData.options}
            recommendedMode={commuteData.recommended_option.mode}
          />

          <ProvenancesDrawer options={commuteData.options} />
        </>
      )}

      <footer style={{ textAlign: 'center', marginTop: '3rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
        Smart Commute Chennai MVP &copy; 2026. All transit fares and emission factors are source-backed with transparent provenance.
      </footer>
    </div>
  );
}
