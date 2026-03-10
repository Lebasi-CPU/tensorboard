import React, { useEffect, useState } from 'react';
// Leaflet and Socket.IO would need to be installed in a real environment
// import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
// import { io } from 'socket.io-client';

interface Emergency {
  id: string;
  type: 'fire' | 'flood' | 'earthquake' | 'medical' | 'accident';
  priority: 'low' | 'medium' | 'high' | 'critical';
  location: { lat: number; lon: number };
  prediction_confidence: number;
  estimated_resources_needed: string[];
  timestamp: string;
}

export const EmergencyMap: React.FC = () => {
  const [emergencies, setEmergencies] = useState<Emergency[]>([]);

  useEffect(() => {
    // Conectar a WebSocket para updates en tiempo real
    // const newSocket = io('ws://emergency-ai.example.com');
    console.log("Conectando al Sistema de Emergencias Real-Time...");

    // Simulación de notificación para una emergencia crítica
    const timer = setTimeout(() => {
        const dummy: Emergency = {
            id: "1", type: "fire", priority: "critical",
            location: {lat: 40.71, lon: -74.00},
            prediction_confidence: 0.98,
            estimated_resources_needed: ["Bomberos", "Ambulancia"],
            timestamp: new Date().toISOString()
        };
        setEmergencies([dummy]);
        if (Notification.permission === 'granted') {
             new Notification('🚨 Emergencia Crítica Detectada', {
                body: `${dummy.type} en ${dummy.location.lat}, ${dummy.location.lon}`,
                icon: '/emergency-icon.png'
             });
        }
    }, 5000);

    return () => clearTimeout(timer);
  }, []);

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return '#FF0000';
      case 'high': return '#FF6600';
      case 'medium': return '#FFCC00';
      case 'low': return '#00FF00';
      default: return '#808080';
    }
  };

  return (
    <div className="emergency-map-container">
      <div className="map-header">
        <h2>🚨 Sistema de IA para Emergencias - Vista en Tiempo Real</h2>
        <div className="stats">
          <span>Total: {emergencies.length}</span>
          <span>Críticas: {emergencies.filter(e => e.priority === 'critical').length}</span>
        </div>
      </div>
      <div className="map-placeholder" style={{height: '500px', background: '#e0e0e0', display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
           [ Mapa de Emergencias NEXUS v1.0 ]
           {emergencies.map(e => (
               <div key={e.id} style={{border: '1px solid black', padding: '10px', background: 'white'}}>
                    <h3>🚨 {e.type.toUpperCase()}</h3>
                    <p style={{color: getPriorityColor(e.priority)}}>Prioridad: {e.priority}</p>
                    <p>Confianza: {(e.prediction_confidence * 100).toFixed(1)}%</p>
               </div>
           ))}
      </div>
    </div>
  );
};
