export default function SourceFilter({ sources = [], selected = [], onChange }) {
  return (
    <div>
      {sources.map((source) => (
        <label key={source} style={{ marginRight: 12 }}>
          <input
            type="checkbox"
            checked={selected.includes(source)}
            onChange={() => onChange?.(source)}
          />
          {" "}{source}
        </label>
      ))}
    </div>
  );
}
