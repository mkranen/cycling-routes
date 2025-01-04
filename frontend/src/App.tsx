import "maplibre-gl/dist/maplibre-gl.css";
import React from "react";
import Map from "./components/map/Map";
import Header from "./components/navigation/Header";
import Sidebar from "./components/navigation/Sidebar";
import Route from "./components/routes/Route";

function App() {
    return (
        <div className="h-dvh w-dvw">
            <Header />
            <div className="absolute bottom-0 left-0 right-0 flex flex-row top-16 bg-base-100">
                <div className="w-96 shrink-0">
                    <Sidebar />
                </div>
                <div className="relative flex flex-row w-full h-full">
                    <div className="absolute top-0 bottom-0 left-0 right-0">
                        <Map />
                        <div className="absolute flex flex-row right-4 top-4">
                            <Route />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
export default App;
