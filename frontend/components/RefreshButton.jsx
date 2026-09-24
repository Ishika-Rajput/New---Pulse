export default function RefreshButton({ onRefresh, loading = false }) {
  return (
    <button onClick={onRefresh} disabled={loading}>
      {loading ? "Refreshing..." : "Refresh data"}
    </button>
  );
}
