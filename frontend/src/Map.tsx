import "leaflet/dist/leaflet.css";
import React, { useRef } from "react";
import { MapContainer, TileLayer } from "react-leaflet";

const Map = () => {
  const mapRef = useRef(null);
  const latitude = 52.11015993159475;
  const longitude = 5.13381188435385;

  return (
    <MapContainer center={[latitude, longitude]} zoom={13} ref={mapRef} style={{ height: "100vh", width: "100vw" }}>
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
    </MapContainer>
  );
};

export default Map;
