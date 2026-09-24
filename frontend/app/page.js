"use client";

import { useEffect, useMemo, useState } from "react";
import {
  getTimeline,
  getCluster,
  triggerIngestion,
  getIngestionStatus,
} from "../lib/api";

const TIMELINE_WIDTH = 4000;
const CARD_WIDTH = 120;
const CARD_GAP = 20;
const LANE_COUNT = 4;

const SOURCES = ["All", "BBC", "NPR", "Guardian"];

export default function Home() {
  const [timeline, setTimeline] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedCluster, setSelectedCluster] = useState(null);
  const [clusterLoading, setClusterLoading] = useState(false);

  const [selectedSource, setSelectedSource] = useState("All");
  const [refreshing, setRefreshing] = useState(false);

  async function loadTimeline() {
    try {
      setLoading(true);
      setError("");

      const data = await getTimeline();
      setTimeline(data);
    } catch (err) {
      console.error(err);
      setError("Unable to load the news timeline.");
    } finally {
      setLoading(false);
    }
  }
  async function refreshData() {
  try {
    setRefreshing(true);
    setError("");

    // Start ingestion
    const job = await triggerIngestion();

    // Poll ingestion status
    let status = "queued";

    while (status === "queued" || status === "running") {
      await new Promise((resolve) =>
        setTimeout(resolve, 3000)
      );

      const result = await getIngestionStatus(job.jobId);

      status = result.status;

      if (status === "failed") {
        throw new Error(
          result.error || "Ingestion failed"
        );
      }
    }

    // Ingestion completed successfully.
    // Reload the latest timeline data.
    await loadTimeline();

  } catch (err) {
    console.error(err);
    setError(
      "Unable to refresh news data. Please try again."
    );
  } finally {
    setRefreshing(false);
  }
}
  async function openCluster(id) {
    try {
      setClusterLoading(true);
      setError("");

      const data = await getCluster(id);
      setSelectedCluster(data);
    } catch (err) {
      console.error(err);
      setError("Unable to load cluster details.");
    } finally {
      setClusterLoading(false);
    }
  }

  useEffect(() => {
    loadTimeline();
  }, []);

  /*
   * Filter clusters according to selected source.
   *
   * A cluster remains visible if the selected source
   * is one of the sources covering that cluster.
   */
  const filteredTimeline = useMemo(() => {
    if (selectedSource === "All") {
      return timeline;
    }

    return timeline.filter((item) =>
      item.sources?.includes(selectedSource)
    );
  }, [timeline, selectedSource]);

  /*
   * Calculate the time range from the FILTERED
   * timeline so the selected source fills the
   * available timeline naturally.
   */
  const timelineRange = useMemo(() => {
    if (!filteredTimeline.length) {
      return null;
    }

    const timestamps = filteredTimeline.flatMap((item) => [
      new Date(item.start).getTime(),
      new Date(item.end).getTime(),
    ]);

    return {
      min: Math.min(...timestamps),
      max: Math.max(...timestamps),
    };
  }, [filteredTimeline]);

  /*
   * Convert article time to horizontal position.
   */
  function getXPosition(item) {
    if (!timelineRange) {
      return 0;
    }

    const start = new Date(item.start).getTime();

    const range =
      timelineRange.max - timelineRange.min || 1;

    const percentage =
      (start - timelineRange.min) / range;

    return percentage * TIMELINE_WIDTH;
  }

  /*
   * Arrange cards into multiple lanes.
   *
   * This prevents cards from sitting directly
   * on top of each other when several stories
   * happen close together.
   */
  const clusterLayout = useMemo(() => {
    if (!filteredTimeline.length) {
      return [];
    }

    const sorted = [...filteredTimeline].sort(
      (a, b) =>
        new Date(a.start).getTime() -
        new Date(b.start).getTime()
    );

    const laneLastX = Array(LANE_COUNT).fill(
      -Infinity
    );

    return sorted.map((item) => {
      let x = getXPosition(item);

      let selectedLane = -1;

      /*
       * Find the first lane with enough
       * horizontal space.
       */
      for (
        let lane = 0;
        lane < LANE_COUNT;
        lane++
      ) {
        if (
          x >=
          laneLastX[lane] +
            CARD_WIDTH +
            CARD_GAP
        ) {
          selectedLane = lane;
          break;
        }
      }

      /*
       * If all lanes are occupied, use the
       * lane whose previous card finishes first.
       */
      if (selectedLane === -1) {
        selectedLane = laneLastX.indexOf(
          Math.min(...laneLastX)
        );

        x =
          laneLastX[selectedLane] +
          CARD_WIDTH +
          CARD_GAP;
      }

      laneLastX[selectedLane] = x;

      return {
        ...item,
        x,
        lane: selectedLane,
      };
    });
  }, [filteredTimeline, timelineRange]);

  if (loading) {
    return (
      <main className="page">
        <h1>News Pulse</h1>
        <p>Loading news timeline...</p>
      </main>
    );
  }

  if (error && !timeline.length) {
    return (
      <main className="page">
        <h1>News Pulse</h1>

        <p className="error">{error}</p>

        <button onClick={loadTimeline}>
          Retry
        </button>
      </main>
    );
  }

  return (
    <main className="page">

      {/* HEADER */}

      <header className="header">

        <div>
          <h1>News Pulse</h1>

          <p>
            Topic-clustered news timeline
          </p>
        </div>

        <button
  onClick={refreshData}
  disabled={refreshing}
>
  {refreshing
    ? "Refreshing News..."
    : "Refresh Data"}
</button>

      </header>


      {/* SOURCE FILTER */}

      <section className="source-filter">

        <div className="source-filter-title">
          Filter by source
        </div>

        <div className="source-buttons">

          {SOURCES.map((source) => (
            <button
              key={source}
              className={
                selectedSource === source
                  ? "source-button active"
                  : "source-button"
              }
              onClick={() =>
                setSelectedSource(source)
              }
            >
              {source === "All"
                ? "All Sources"
                : source}
            </button>
          ))}

        </div>

      </section>


      {/* TIMELINE */}

      <section className="timeline-section">

        <div className="timeline-header">

          <span>
            {filteredTimeline.length} topic{" "}
            {filteredTimeline.length === 1
              ? "cluster"
              : "clusters"}
          </span>

          {selectedSource !== "All" && (
            <span>
              {" "}
              • Showing {selectedSource}
            </span>
          )}

        </div>


        {filteredTimeline.length === 0 ? (

          <div className="empty-state">
            <h3>No clusters found</h3>

            <p>
              There are no topic clusters from{" "}
              {selectedSource}.
            </p>
          </div>

        ) : (

          <div
            className="timeline"
            style={{
              width: `${TIMELINE_WIDTH}px`,
              height: "560px",
            }}
          >

            {/* Main timeline line */}

            <div className="timeline-line" />


            {/* Cluster cards */}

            {clusterLayout.map((item) => {

              const top =
                30 + item.lane * 115;

              return (
                <button
                  key={item.id}
                  className="cluster-block"
                  style={{
                    left: `${item.x}px`,
                    top: `${top}px`,
                  }}
                  onClick={() =>
                    openCluster(item.id)
                  }
                >

                  <span className="cluster-label">
                    {item.label}
                  </span>

                  <span className="cluster-count">
                    {item.count}{" "}
                    {item.count === 1
                      ? "article"
                      : "articles"}
                  </span>

                </button>
              );
            })}

          </div>

        )}

      </section>


      {/* ERROR */}

      {error && timeline.length > 0 && (
        <p className="error">
          {error}
        </p>
      )}


      {/* CLUSTER LOADING */}

      {clusterLoading && (
        <div className="details-panel">
          Loading cluster...
        </div>
      )}


      {/* CLUSTER DETAILS */}

      {selectedCluster &&
        !clusterLoading && (

          <section className="details-panel">

            <div className="details-header">

              <div>

                <h2>
                  {selectedCluster.label}
                </h2>

                <p>
                  {selectedCluster.articles.length}{" "}
                  {selectedCluster.articles.length === 1
                    ? "article"
                    : "articles"}
                </p>

              </div>


              <button
                onClick={() =>
                  setSelectedCluster(null)
                }
              >
                Close
              </button>

            </div>


            <div className="article-list">

              {selectedCluster.articles.map(
                (article) => (

                  <article
                    key={article.id}
                    className="article-card"
                  >

                    <div className="article-source">
                      {article.source}
                    </div>

                    <h3>
                      {article.headline}
                    </h3>

                    <p>
                      {article.published_at
                        ? new Date(
                            article.published_at
                          ).toLocaleString()
                        : "Unknown time"}
                    </p>

                    <a
                      href={article.url}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      Read original article →
                    </a>

                  </article>

                )
              )}

            </div>

          </section>

        )}

    </main>
  );
}