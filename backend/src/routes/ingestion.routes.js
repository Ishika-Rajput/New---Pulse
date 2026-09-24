import { Router } from "express";
import { randomUUID } from "crypto";
import { spawn } from "child_process";
import path from "path";
import { fileURLToPath } from "url";

const router = Router();

const jobs = new Map();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/*
 * Project structure:
 *
 * news-pulse/
 * ├── backend/
 * │   └── src/routes/ingestion.routes.js
 * │
 * └── scraper/
 *     ├── main.py
 *     └── .venv/
 *         └── Scripts/
 *             └── python.exe
 */

const projectRoot = path.resolve(
  __dirname,
  "../../.."
);

const pythonExecutable =
  process.env.PYTHON_EXECUTABLE ||
  (process.platform === "win32"
    ? path.join(
        projectRoot,
        "scraper",
        ".venv",
        "Scripts",
        "python.exe"
      )
    : "python3");

const scraperScript = path.join(
  projectRoot,
  "scraper",
  "main.py"
);


/*
 * POST /ingest/trigger
 */
router.post("/trigger", (_req, res) => {
  const jobId = randomUUID();

  jobs.set(jobId, {
    status: "queued",
    startedAt: null,
    completedAt: null,
    output: "",
    error: null,
  });

  res.status(202).json({
    jobId,
    status: "queued",
  });

  /*
   * Start Python after sending the response.
   */
  const pythonProcess = spawn(
    pythonExecutable,
    [scraperScript],
    {
      cwd: projectRoot,
      windowsHide: true,
      env: {
        ...process.env,
      },
    }
  );

  jobs.set(jobId, {
    status: "running",
    startedAt: new Date().toISOString(),
    completedAt: null,
    output: "",
    error: null,
  });

  /*
   * Capture normal Python output.
   */
  pythonProcess.stdout.on("data", (data) => {
    const job = jobs.get(jobId);

    if (!job) return;

    job.output += data.toString();

    jobs.set(jobId, job);
  });


  /*
   * Capture Python errors.
   */
  pythonProcess.stderr.on("data", (data) => {
    const job = jobs.get(jobId);

    if (!job) return;

    job.error =
      (job.error || "") +
      data.toString();

    jobs.set(jobId, job);
  });


  /*
   * Python process finished.
   */
  pythonProcess.on("close", (code) => {
    const job = jobs.get(jobId);

    if (!job) return;

    job.completedAt =
      new Date().toISOString();

    if (code === 0) {
      job.status = "completed";
    } else {
      job.status = "failed";

      if (!job.error) {
        job.error =
          `Python process exited with code ${code}`;
      }
    }

    jobs.set(jobId, job);
  });


  /*
   * Python process could not start.
   */
  pythonProcess.on("error", (error) => {
    const job = jobs.get(jobId);

    if (!job) return;

    job.status = "failed";

    job.completedAt =
      new Date().toISOString();

    job.error = error.message;

    jobs.set(jobId, job);
  });
});


/*
 * GET /ingest/status/:jobId
 */
router.get(
  "/status/:jobId",
  (req, res) => {
    const job =
      jobs.get(req.params.jobId);

    if (!job) {
      return res.status(404).json({
        error: "Job not found",
      });
    }

    res.json({
      jobId: req.params.jobId,
      ...job,
    });
  }
);

export default router;