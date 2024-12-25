import React from "react";
import Map from "./Map";

function App() {
  return (
    <div className="h-dvh w-dvw">
      <h1 className="flex items-center h-16 p-4 text-3xl">Cycling routes</h1>
      <div className="absolute bottom-0 left-0 right-0 top-16">
        <Map />
      </div>
    </div>
  );
}
export default App;
