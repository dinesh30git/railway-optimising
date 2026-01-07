export default function RailwayNetworkView({ trains, setTrains }) {

  function handleFileUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();

    reader.onload = () => {
      const lines = reader.result.trim().split("\n");
      const headers = lines[0].split(",");

      const data = lines.slice(1).map(line => {
        const values = line.split(",");
        const obj = {};
        headers.forEach((h, i) => {
          obj[h.trim()] = values[i]?.trim();
        });
        return obj;
      });

      console.log("CSV parsed trains:", data); // 🔴 DEBUG LINE
      setTrains(data); // 🔴 THIS IS CRITICAL
    };

    reader.readAsText(file);
  }

  return (
    <>
      <input type="file" accept=".csv" onChange={handleFileUpload} />

      <svg width="100%" height="140">
        <line x1="50" y1="50" x2="550" y2="50" stroke="black" />
        <line x1="50" y1="80" x2="550" y2="80" stroke="black" />

        {["Ehw", "Gp", "Hze", "Mz", "Wt"].map((b, i) => (
          <g key={b}>
            <circle cx={100 + i * 100} cy={65} r="4" fill="black" />
            <text x={90 + i * 100} y={110} fontSize="12">{b}</text>
          </g>
        ))}

        {trains.map((t, i) => (
          <circle
            key={i}
            cx={100 + ["Ehw","Gp","Hze","Mz","Wt"].indexOf(t.current_block) * 100}
            cy={t.line_type === "UP" ? 45 : 85}
            r="6"
            fill="orange"
          />
        ))}
      </svg>
    </>
  );
}
