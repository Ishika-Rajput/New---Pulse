import { Router } from "express";
import pool from "../config/database.js";

const router = Router();


// GET /clusters
router.get("/", async (_req, res) => {
  try {

    const result = await pool.query(`
      SELECT
        c.id,
        c.label,
        COUNT(ca.article_id)::int AS article_count
      FROM clusters c
      LEFT JOIN cluster_articles ca
        ON c.id = ca.cluster_id
      GROUP BY c.id, c.label
      ORDER BY c.id;
    `);

    res.json(result.rows);

  } catch (error) {

    console.error("Error fetching clusters:", error);

    res.status(500).json({
      error: "Failed to fetch clusters"
    });

  }
});


// GET /clusters/:id
router.get("/:id", async (req, res) => {

  try {

    const clusterId = Number(req.params.id);

    if (!Number.isInteger(clusterId)) {
      return res.status(400).json({
        error: "Invalid cluster ID"
      });
    }

    const clusterResult = await pool.query(
      `
      SELECT
        id,
        label,
        created_at
      FROM clusters
      WHERE id = $1;
      `,
      [clusterId]
    );

    if (clusterResult.rows.length === 0) {
      return res.status(404).json({
        error: `Cluster ${clusterId} not found`
      });
    }

    const articlesResult = await pool.query(
      `
      SELECT
        a.id,
        a.source,
        a.headline,
        a.summary,
        a.url,
        a.published_at
      FROM articles a
      INNER JOIN cluster_articles ca
        ON a.id = ca.article_id
      WHERE ca.cluster_id = $1
      ORDER BY a.published_at DESC NULLS LAST;
      `,
      [clusterId]
    );

    res.json({
      ...clusterResult.rows[0],
      articles: articlesResult.rows
    });

  } catch (error) {

  console.error("Error fetching clusters:", error);

  res.status(500).json({
    error: "Failed to fetch clusters",
    details: error.message
  });

}
});

export default router;