import cors from "cors";
import express from "express";
import { Pool } from "pg";
import { WebSocketServer } from "ws";
import { routeRouter } from "./routes/routes";

const app = express();
const port = process.env.PORT || 3000;

// Database connection
export const pool = new Pool({
    user: "cycling-routes",
    host: "localhost",
    database: "cycling-routes",
    password: "HYr5xe9j6cYANf",
    port: 5432,
});

// Middleware
app.use(cors());
app.use(express.json());

// WebSocket setup
const wss = new WebSocketServer({ port: 8080 });

wss.on("connection", (ws) => {
    ws.on("message", (data) => {
        wss.clients.forEach((client) => {
            client.send(data.toString());
        });
    });
});

// Routes
app.use("/api", routeRouter);

app.listen(port, () => {
    console.log(`Server running on port ${port}`);
});
