import "maplibre-gl/dist/maplibre-gl.css";
import React from "react";
import Map from "./components/map/Map";
import Sidebar from "./components/routes/Sidebar";

function App() {
    return (
        <div className="h-dvh w-dvw">
            <div className="h-16 p-4 navbar bg-base-300">
                <div className="text-3xl">Cycling routes</div>
            </div>
            <div className="flex flex-row w-full h-full bg-base-100">
                <div className="w-96">
                    <Sidebar />
                </div>
                <div className="relative flex flex-row w-full h-full">
                    <div className="absolute top-0 left-0 right-0 bottom-16">
                        <Map />
                    </div>
                </div>
            </div>
        </div>
    );
}
export default App;
