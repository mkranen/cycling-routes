import { GeolocateControl, Map as MaplibreMap } from "@vis.gl/react-maplibre";
import React from "react";
import { useDispatch, useSelector } from "react-redux";
import { RootState } from "../../store";
import { setLatitude, setLongitude } from "./mapSlice";

function Map() {
  const latitude = useSelector((state: RootState) => state.map.latitude);
  const longitude = useSelector((state: RootState) => state.map.longitude);
  const zoom = useSelector((state: RootState) => state.map.zoom);
  const dispatch = useDispatch();

  const [viewState, setViewState] = React.useState({
    longitude,
    latitude,
    zoom,
  });

  return (
    <MaplibreMap
      {...viewState}
      className="w-full h-full"
      onMove={(evt) => setViewState(evt.viewState)}
      mapStyle={`https://api.maptiler.com/maps/streets/style.json?key=${import.meta.env.VITE_MAPTILER_KEY}`}
    >
      <GeolocateControl
        positionOptions={{ enableHighAccuracy: true }}
        showAccuracyCircle={true}
        position="bottom-right"
        onGeolocate={(event) => {
          dispatch(setLongitude(event.coords.longitude));
          dispatch(setLatitude(event.coords.latitude));
        }}
        onError={(error) => {
          console.log(error);
        }}
      />
    </MaplibreMap>
  );
}
export default Map;
