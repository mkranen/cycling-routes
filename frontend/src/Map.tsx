import { GeolocateControl, Map as MaplibreMap } from "@vis.gl/react-maplibre";
import "maplibre-gl/dist/maplibre-gl.css";
import React from "react";

function Map() {
  const [viewState, setViewState] = React.useState({
    longitude: 5.13381188435385,
    latitude: 52.11015993159475,
    zoom: 15,
  });

  return (
    <MaplibreMap
      {...viewState}
      reuseMaps={true}
      className="w-full h-full"
      onMove={(evt) => setViewState(evt.viewState)}
      mapStyle={`https://api.maptiler.com/maps/streets/style.json?key=${import.meta.env.VITE_MAPTILER_KEY}`}
    >
      <GeolocateControl
        positionOptions={{ enableHighAccuracy: true }}
        trackUserLocation={true}
        showAccuracyCircle={true}
        position="bottom-right"
        showUserHeading={true}
      />

      {/* <Marker longitude={5.13381188435385} latitude={52.11015993159475} anchor="bottom"></Marker> */}
    </MaplibreMap>
  );
}
export default Map;
