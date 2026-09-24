export default function TimelineCluster({ cluster }) {
  return <div>{cluster?.label ?? "Topic"}</div>;
}
