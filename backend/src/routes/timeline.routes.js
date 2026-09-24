import { Router } from "express";
import pool from "../config/database.js";

const router = Router();

router.get("/", async (_req, res) => {
  try {
    const result = await pool.query(`
      SELECT
        c.id,
        c.label,
        MIN(a.published_at) AS start,
        MAX(a.published_at) AS "end",
        COUNT(a.id)::int AS count,
        COUNT(a.id)::int AS intensity,
        ARRAY_AGG(DISTINCT a.source) AS sources
      FROM clusters c
      INNER JOIN cluster_articles ca
        ON c.id = ca.cluster_id
      INNER JOIN articles a
        ON ca.article_id = a.id
      WHERE a.published_at IS NOT NULL
      GROUP BY c.id, c.label
      ORDER BY start ASC;
    `);

    res.json(result.rows);
  } catch (error) {
    console.error("Error fetching timeline:", error);

    res.status(500).json({
      error: "Failed to fetch timeline",
      details: error.message,
    });
  }
});

export default router;