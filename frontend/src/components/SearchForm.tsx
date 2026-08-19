import React, { useState } from 'react';
import { Search, Navigation, Settings } from 'lucide-react';

interface SearchFormProps {
  onSearch: (params: {
    originText: string;
    destinationText: string;
    priority: string;
    bikeMileage: number;
  }) => void;
  petrolPrice: number;
  onUpdatePetrolPrice: (price: number) => void;
  loading: boolean;
}

export const SearchForm: React.FC<SearchFormProps> = ({
  onSearch,
  petrolPrice,
  onUpdatePetrolPrice,
  loading
}) => {
  const [originText, setOriginText] = useState('VIT Chennai');
  const [destinationText, setDestinationText] = useState('Chennai Central');
  const [priority, setPriority] = useState('best_overall');
  const [bikeMileage, setBikeMileage] = useState(45.0);
  const [isEditingPrice, setIsEditingPrice] = useState(false);
  const [tempPrice, setTempPrice] = useState(petrolPrice.toString());

  const handlePreset = (orig: string, dest: string) => {
    setOriginText(orig);
    setDestinationText(dest);
    onSearch({ originText: orig, destinationText: dest, priority, bikeMileage });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch({ originText, destinationText, priority, bikeMileage });
  };

  const handlePriceSave = () => {
    const val = parseFloat(tempPrice);
    if (!isNaN(val) && val > 0) {
      onUpdatePetrolPrice(val);
      setIsEditingPrice(false);
    }
  };

  return (
    <div className="glass-card">
      <div className="banner">
        <span>
          <strong>Petrol price used for estimate:</strong> ₹{petrolPrice.toFixed(2)} / Litre (Configurable Parameter)
        </span>
        {isEditingPrice ? (
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <input
              type="number"
              style={{ width: '80px', padding: '0.2rem 0.5rem' }}
              value={tempPrice}
              onChange={(e) => setTempPrice(e.target.value)}
            />
            <button className="preset-btn" onClick={handlePriceSave}>Save</button>
          </div>
        ) : (
          <button className="preset-btn" onClick={() => setIsEditingPrice(true)}>
            <Settings size={14} style={{ display: 'inline', marginRight: '4px' }} /> Edit Parameter
          </button>
        )}
      </div>

      <div className="presets-container">
        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', alignSelf: 'center' }}>Demo Journeys:</span>
        <button className="preset-btn" onClick={() => handlePreset('VIT Chennai', 'Chennai Central')}>
          VIT Chennai → Central
        </button>
        <button className="preset-btn" onClick={() => handlePreset('Chennai Airport', 'Guindy')}>
          Airport → Guindy
        </button>
        <button className="preset-btn" onClick={() => handlePreset('Tambaram', 'Chennai Central')}>
          Tambaram → Central
        </button>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="form-grid">
          <div className="form-group">
            <label><Navigation size={14} style={{ display: 'inline', marginRight: '4px' }} /> Origin Location</label>
            <input
              type="text"
              value={originText}
              onChange={(e) => setOriginText(e.target.value)}
              placeholder="e.g. VIT Chennai, Airport, Guindy..."
              required
            />
          </div>

          <div className="form-group">
            <label><Navigation size={14} style={{ display: 'inline', marginRight: '4px' }} /> Destination</label>
            <input
              type="text"
              value={destinationText}
              onChange={(e) => setDestinationText(e.target.value)}
              placeholder="e.g. Chennai Central, Alandur..."
              required
            />
          </div>

          <div className="form-group">
            <label>Bike Mileage (km/L)</label>
            <input
              type="number"
              step="1"
              value={bikeMileage}
              onChange={(e) => setBikeMileage(parseFloat(e.target.value) || 45)}
            />
          </div>

          <div className="form-group">
            <label>Optimization Preference</label>
            <select value={priority} onChange={(e) => setPriority(e.target.value)}>
              <option value="best_overall">Best Overall (Balanced)</option>
              <option value="fastest">Fastest Journey Time</option>
              <option value="cheapest">Cheapest Travel Cost</option>
              <option value="greenest">Greenest (Lowest CO2)</option>
            </select>
          </div>
        </div>

        <button type="submit" className="btn-primary" disabled={loading}>
          <Search size={18} /> {loading ? 'Computing Route Options...' : 'Compare Commute Options'}
        </button>
      </form>
    </div>
  );
};
