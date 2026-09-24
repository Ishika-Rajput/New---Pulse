const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000";

export async function getClusters() {
  const response = await fetch(`${API_URL}/clusters`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Failed to fetch clusters");
  }

  return response.json();
}

export async function getCluster(id) {
  const response = await fetch(`${API_URL}/clusters/${id}`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Failed to fetch cluster");
  }

  return response.json();
}

export async function getTimeline() {
  const response = await fetch(`${API_URL}/timeline`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Failed to fetch timeline");
  }

  return response.json();
}

export async function triggerIngestion() {
  const response = await fetch(`${API_URL}/ingest/trigger`, {
    method: "POST",
  });

  if (!response.ok) {
    throw new Error("Failed to trigger ingestion");
  }

  return response.json();
}

export async function getIngestionStatus(jobId) {
  const response = await fetch(
    `${API_URL}/ingest/status/${jobId}`,
    {
      cache: "no-store",
    }
  );

  if (!response.ok) {
    throw new Error("Failed to fetch ingestion status");
  }

  return response.json();
}