import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';

// Custom marker icons
const originIcon = L.divIcon({
  className: 'custom-map-icon',
  html: `<div style="background-color: #38bdf8; width: 14px; height: 14px; border-radius: 50%; border: 3px solid #ffffff; box-shadow: 0 0 10px rgba(56, 189, 248, 0.8);"></div>`,
  iconSize: [14, 14],
  iconAnchor: [7, 7]
});

const destIcon = L.divIcon({
  className: 'custom-map-icon',
  html: `<div style="background-color: #f43f5e; width: 14px; height: 14px; border-radius: 50%; border: 3px solid #ffffff; box-shadow: 0 0 10px rgba(244, 63, 94, 0.8);"></div>`,
  iconSize: [14, 14],
  iconAnchor: [7, 7]
});

interface RouteMapProps {
  origin: { lat: number; lng: number; text: string };
  destination: { lat: number; lng: number; text: string };
}

function RecenterMap({ lat1, lng1, lat2, lng2 }: { lat1: number; lng1: number; lat2: number; lng2: number }) {
  const map = useMap();
  useEffect(() => {
    const bounds = L.latLngBounds([[lat1, lng1], [lat2, lng2]]);
    map.fitBounds(bounds, { padding: [40, 40] });
  }, [lat1, lng1, lat2, lng2, map]);
  return null;
}

export const RouteMap: React.FC<RouteMapProps> = ({ origin, destination }) => {
  const centerLat = (origin.lat + destination.lat) / 2;
  const centerLng = (origin.lng + destination.lng) / 2;

  const positions: [number, number][] = [
    [origin.lat, origin.lng],
    [destination.lat, destination.lng]
  ];

  return (
    <div style={{ position: 'relative' }}>
      <MapContainer
        center={[centerLat, centerLng]}
        zoom={12}
        scrollWheelZoom={false}
        className="leaflet-container"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <Marker position={[origin.lat, origin.lng]} icon={originIcon}>
          <Popup>Origin: {origin.text}</Popup>
        </Marker>
        <Marker position={[destination.lat, destination.lng]} icon={destIcon}>
          <Popup>Destination: {destination.text}</Popup>
        </Marker>
        <Polyline positions={positions} color="#38bdf8" weight={3} dashArray="5, 8" />
        <RecenterMap lat1={origin.lat} lng1={origin.lng} lat2={destination.lat} lng2={destination.lng} />
      </MapContainer>
    </div>
  );
};
