/** @type {import('tailwindcss').Config} */
import daisyui from "daisyui";
import daisyuiColors from "daisyui/src/theming/themes";

export default {
    content: ["./public/index.html", "./src/**/*.{js,ts,jsx,tsx}"],
    daisyui: {
        themes: [
            {
                light: {
                    ...daisyuiColors.light,
                    primary: "#06b6d4",

                    ".btn-primary": {
                        color: "#fff",
                    },
                    ".btn-komoot": {
                        "background-color": "#4F850D",
                        "border-color": "#4F850D",
                    },
                    ".btn-strava": {
                        "background-color": "#fc5200",
                        "border-color": "#fc5200",
                    },
                    ".badge-komoot": {
                        "background-color": "#4F850D",
                        "border-color": "#4F850D",
                        color: "#fff",
                    },
                    ".badge-strava": {
                        "background-color": "#fc5200",
                        "border-color": "#fc5200",
                        color: "#fff",
                    },
                },
            },
        ],
    },
    theme: {
        extend: {
            colors: {
                komoot: "oklch(0.5574 0.1513 132.58 / 1)",
                // komoot: "#4F850D",
                strava: "oklch(0.6678 0.2169 38.35 / 1)",
                // strava: "#fc5200",
            },
            backgroundImage: {
                "gradient-45": "linear-gradient(45deg, var(--tw-gradient-stops))",
                "gradient-90": "linear-gradient(90deg, var(--tw-gradient-stops))",
                "gradient-135": "linear-gradient(135deg, var(--tw-gradient-stops))",
                "gradient-180": "linear-gradient(180deg, var(--tw-gradient-stops))",
                "gradient-225": "linear-gradient(225deg, var(--tw-gradient-stops))",
                "gradient-270": "linear-gradient(270deg, var(--tw-gradient-stops))",
                "gradient-315": "linear-gradient(315deg, var(--tw-gradient-stops))",
            },
        },
    },
    plugins: [daisyui],
};
