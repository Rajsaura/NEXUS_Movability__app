import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Database, ShieldCheck } from 'lucide-react';

interface ProvenanceMetric {
  value?: any;
  unit: string;
  source_type: string;
  confidence: string;
}

interface TransportOption {
  mode: string;
  is_supported: boolean;
  provenance: {
    distance: ProvenanceMetric;
    duration: ProvenanceMetric;
    fare: ProvenanceMetric;
    co2: ProvenanceMetric;
  };
  assumptions: string[];
}

interface ProvenancesDrawerProps {
  options: TransportOption[];
}

export const ProvenancesDrawer: React.FC<ProvenancesDrawerProps> = ({ options }) => {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <div className="assumptions-section">
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          width: '100%',
          background: 'none',
          border: 'none',
          color: 'var(--accent-cyan)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          fontSize: '1.1rem',
          fontWeight: 600,
          cursor: 'pointer',
          padding: '0.5rem 0'
        }}
      >
        <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Database size={18} /> Data Sources, Provenance & Scientific Assumptions
        </span>
        {isOpen ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
      </button>

      {isOpen && (
        <div style={{ marginTop: '1rem' }}>
          <div style={{ background: 'rgba(56, 189, 248, 0.08)', border: '1px solid rgba(56, 189, 248, 0.2)', padding: '0.75rem 1rem', borderRadius: '0.5rem', marginBottom: '1rem', fontSize: '0.85rem', color: '#e2e8f0' }}>
            <ShieldCheck size={16} style={{ display: 'inline', marginRight: '6px', color: 'var(--accent-cyan)' }} />
            <strong>Mandatory Verification Notice:</strong> All carbon emission metrics displayed in this application are strictly labeled 
            <em style={{ color: 'var(--accent-green)', marginLeft: '4px' }}>"Estimated CO2 based on documented assumptions"</em>.
          </div>

          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Transport Mode</th>
                  <th>Metric</th>
                  <th>Value</th>
                  <th>Source Type Provenance</th>
                  <th>Confidence</th>
                </tr>
              </thead>
              <tbody>
                {options.filter(o => o.is_supported).map((opt) => (
                  <React.Fragment key={opt.mode}>
                    <tr>
                      <td rowSpan={4} style={{ fontWeight: 600, verticalAlign: 'top', background: 'rgba(15, 23, 42, 0.4)' }}>
                        {opt.mode}
                      </td>
                      <td>Distance</td>
                      <td>{opt.provenance.distance.value} {opt.provenance.distance.unit}</td>
                      <td><code>{opt.provenance.distance.source_type}</code></td>
                      <td><span className={`badge-tag badge-${opt.provenance.distance.confidence.toLowerCase()}`}>{opt.provenance.distance.confidence}</span></td>
                    </tr>
                    <tr>
                      <td>Duration</td>
                      <td>{opt.provenance.duration.value} {opt.provenance.duration.unit}</td>
                      <td><code>{opt.provenance.duration.source_type}</code></td>
                      <td><span className={`badge-tag badge-${opt.provenance.duration.confidence.toLowerCase()}`}>{opt.provenance.duration.confidence}</span></td>
                    </tr>
                    <tr>
                      <td>Fare / Fuel Cost</td>
                      <td>₹{opt.provenance.fare.value}</td>
                      <td><code>{opt.provenance.fare.source_type}</code></td>
                      <td><span className={`badge-tag badge-${opt.provenance.fare.confidence.toLowerCase()}`}>{opt.provenance.fare.confidence}</span></td>
                    </tr>
                    <tr>
                      <td>CO2 Emissions</td>
                      <td>{opt.provenance.co2.value} kg</td>
                      <td><code>{opt.provenance.co2.source_type}</code></td>
                      <td><span className={`badge-tag badge-${opt.provenance.co2.confidence.toLowerCase()}`}>{opt.provenance.co2.confidence}</span></td>
                    </tr>
                  </React.Fragment>
                ))}
              </tbody>
            </table>
          </div>

          <div style={{ marginTop: '1.25rem' }}>
            <h4 style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>Documented Domain Assumptions:</h4>
            <ul style={{ listStyleType: 'disc', paddingLeft: '1.25rem', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              <li><strong>Bike Emissions:</strong> Computed dynamically using IPCC 2006 Gasoline carbon coefficient (2.310 kg CO2 / Litre) divided by user bike mileage (Default 45 km/L).</li>
              <li><strong>Metro Fare:</strong> Calculated fare matrix derived from official CMRL fare rules (distance slabs ₹10-₹50), with validation against official spot-check examples.</li>
              <li><strong>Metro Emissions:</strong> Calculated using Central Electricity Authority (CEA) India Grid CO2 Baseline (0.716 kg CO2/kWh) and CMRL Specific Energy Consumption benchmark (0.050 kWh/passenger-km).</li>
              <li><strong>MTC Bus Emissions:</strong> Computed using Heavy Commercial Diesel carbon coefficient (2.68 kg CO2/L) / 3.5 km/L fuel economy / 30 passenger occupancy.</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};
