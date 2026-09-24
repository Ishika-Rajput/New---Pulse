import "dotenv/config";
import express from "express";
import cors from "cors";
import clustersRouter from "./routes/clusters.routes.js";
import timelineRouter from "./routes/timeline.routes.js";
import ingestionRouter from "./routes/ingestion.routes.js";

const app = express();
app.use(cors());
app.use(express.json());

app.get("/health", (_req, res) => res.json({ status: "ok" }));
app.use("/clusters", clustersRouter);
app.use("/timeline", timelineRouter);
app.use("/ingest", ingestionRouter);

const port = process.env.PORT || 4000;
app.listen(port, () => console.log(`API listening on ${port}`));
