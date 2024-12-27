import { GeolocateControl, Map as MaplibreMap } from "@vis.gl/react-maplibre";
import "maplibre-gl/dist/maplibre-gl.css";
import React from "react";

function Map() {
  return (
    <MaplibreMap
      initialViewState={{
        longitude: 5.13381188435385,
        latitude: 52.11015993159475,
        zoom: 15,
      }}
      reuseMaps={true}
      className="w-full h-full"
      mapStyle={`https://api.maptiler.com/maps/streets/style.json?key=${import.meta.env.VITE_MAPTILER_KEY}`}
      //   mapStyle="https://raw.githubusercontent.com/go2garret/maps/main/src/assets/json/openStreetMap.json"
      //   mapStyle="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json"
      // mapStyle="https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json"
      // mapStyle="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
      //   mapStyle="https://geoserveis.icgc.cat/contextmaps/icgc.json"
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
