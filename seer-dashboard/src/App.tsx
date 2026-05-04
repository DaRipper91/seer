import { useState, useEffect } from "react";
import "./App.css";

interface Script {
  name: string;
  description: string;
  tags: string;
  path: string;
  run_count: number;
}

function App() {
  const [scripts, setScripts] = useState<Script[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  const fetchScripts = async (query = "") => {
    try {
      const url = query 
        ? `http://localhost:8888/scripts?query=${encodeURIComponent(query)}`
        : "http://localhost:8888/scripts";
      const response = await fetch(url);
      const data = await response.json();
      setScripts(data.scripts);
    } catch (err) {
      console.error("Failed to fetch scripts:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchScripts();
  }, []);

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setSearch(val);
    fetchScripts(val);
  };

  const executeScript = async (path: string) => {
    try {
      await fetch("http://localhost:8888/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ path, args: [] }),
      });
      // Refresh list to see updated run counts
      fetchScripts(search);
    } catch (err) {
      alert("Failed to manifest script: " + err);
    }
  };

  return (
    <div className="astral-container">
      <div className="header">
        <h1 className="title">🔮 ASTRAL DASHBOARD</h1>
        <input
          type="text"
          className="search-box"
          placeholder="Whisper your intent..."
          value={search}
          onChange={handleSearch}
        />
      </div>

      {loading ? (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
          <p>Consulting the Oracle...</p>
        </div>
      ) : (
        <div className="script-list">
          {scripts.map((script) => (
            <div 
              key={script.path} 
              className="script-card"
              onClick={() => executeScript(script.path)}
            >
              <p className="script-name">{script.name}</p>
              <p className="script-desc">{script.description || "No description found in the timeline."}</p>
              <div className="script-tags">
                {script.tags.split(',').filter(t => t.trim()).map(tag => (
                  <span key={tag} className="tag">{tag.trim()}</span>
                ))}
                <span className="tag" style={{borderColor: '#d7af00', color: '#d7af00'}}>Runs: {script.run_count}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default App;
