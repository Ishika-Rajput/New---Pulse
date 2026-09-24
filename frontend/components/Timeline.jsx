export default function Timeline({ clusters = [] }) {
  return (
    <section>
      {clusters.map((cluster) => (
        <article key={cluster.id}>
          <strong>{cluster.label}</strong>
        </article>
      ))}
    </section>
  );
}
