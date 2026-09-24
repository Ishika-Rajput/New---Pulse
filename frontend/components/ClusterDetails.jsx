export default function ClusterDetails({ cluster }) {
  return <aside>{cluster ? cluster.label : "Select a cluster"}</aside>;
}
