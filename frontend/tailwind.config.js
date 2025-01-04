/** @type {import('tailwindcss').Config} */
import daisyui from "daisyui";
export default {
    content: ["./public/index.html", "./src/**/*.{js,ts,jsx,tsx}"],
    theme: {
        extend: {
            colors: {
                komoot: "oklch(0.5574 0.1513 132.58 / 1)",
                // komoot: "#4F850D",
                strava: "oklch(0.6678 0.2169 38.35 / 1)",
                // strava: "#fc5200",
            },
        },
    },
    plugins: [daisyui],
};
