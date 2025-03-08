import { Router } from "express";
import { pool } from "../server";
import { RouteFilters } from "../types";

const router = Router();

router.get("/routes", async (req, res) => {
    try {
        const {
            sport,
            collections,
            minDistance,
            maxDistance,
            minBounds,
            maxBounds,
            limit = 1000,
        } = req.query as RouteFilters;

        let query = `
      SELECT r.*, 
        json_build_object(
          'id', k.id,
          'name', k.name,
          'sport', k.sport
        ) as komoot
      FROM routes r
      LEFT JOIN komoot_routes k ON r.komoot_id = k.id
      WHERE 1=1
    `;

        const params: any[] = [];
        let paramCount = 1;

        if (minDistance) {
            query += ` AND r.distance >= $${paramCount}`;
            params.push(Number(minDistance) * 1000);
            paramCount++;
        }

        if (maxDistance) {
            query += ` AND r.distance <= $${paramCount}`;
            params.push(Number(maxDistance) * 1000);
            paramCount++;
        }

        if (sport) {
            query += ` AND r.sport = $${paramCount}`;
            params.push(sport);
            paramCount++;
        }

        if (limit) {
            query += ` LIMIT $${paramCount}`;
            params.push(Number(limit));
        }

        const { rows } = await pool.query(query, params);
        res.json(rows);
    } catch (error) {
        console.error("Error fetching routes:", error);
        res.status(500).json({ error: "Internal server error" });
    }
});

export const routeRouter = router;
