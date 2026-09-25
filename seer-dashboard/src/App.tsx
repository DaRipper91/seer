import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Search, Sparkles, Wand2, History, Tag as TagIcon, LayoutGrid } from "lucide-react";
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
  const [castingPath, setCastingPath] = useState<string | null>(null);

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
    setCastingPath(path);
    try {
      await fetch("http://localhost:8888/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ path, args: [] }),
      });
      
      // Simulate incantation time for UX
      setTimeout(() => {
        setCastingPath(null);
        fetchScripts(search);
      }, 1500);
    } catch (err) {
      alert("Failed to manifest script: " + err);
      setCastingPath(null);
    }
  };

  return (
    <div className="astral-container">
      <header className="header">
        <div className="title-group">
          <Sparkles size={28} color="#af87ff" />
          <h1 className="title">ASTRAL DASHBOARD</h1>
        </div>
        
        <div className="search-wrapper">
          <Search className="search-icon" size={18} />
          <input
            type="text"
            className="search-box"
            placeholder="Whisper your intent..."
            value={search}
            onChange={handleSearch}
          />
        </div>
      </header>

      <main className="script-grid">
        <AnimatePresence mode="popLayout">
          {loading ? (
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              style={{ gridColumn: '1/-1', textAlign: 'center', paddingTop: '100px' }}
            >
              <Wand2 className="spinner" style={{ margin: '0 auto 20px' }} />
              <p style={{ color: '#875faf', letterSpacing: '2px' }}>CONSULTING THE ORACLE...</p>
            </motion.div>
          ) : (
            scripts.map((script, index) => (
              <motion.div
                key={script.path}
                layout
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.9 }}
                transition={{ duration: 0.3, delay: index * 0.03 }}
                className="script-card"
                onClick={() => executeScript(script.path)}
              >
                <div className="card-inner">
                  <div className="script-header">
                    <h3 className="script-name">{script.name}</h3>
                    <div className="run-badge">
                      <History size={12} style={{ marginRight: '4px', verticalAlign: 'middle' }} />
                      {script.run_count}
                    </div>
                  </div>
                  
                  <p className="script-desc">
                    {script.description || "No description found in the timeline."}
                  </p>

                  <div className="script-footer">
                    <div className="tags-group">
                      {script.tags.split(',').filter(t => t.trim()).slice(0, 3).map(tag => (
                        <span key={tag} className="tag">
                          <TagIcon size={10} style={{ marginRight: '3px' }} />
                          {tag.trim()}
                        </span>
                      ))}
                    </div>
                    <Wand2 size={16} color="rgba(175, 135, 255, 0.4)" />
                  </div>
                </div>

                <AnimatePresence>
                  {castingPath === script.path && (
                    <motion.div 
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      className="casting-overlay"
                    >
                      <div className="spinner" />
                      <p style={{ fontSize: '10px', color: '#af87ff', letterSpacing: '1px' }}>CASTING...</p>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            ))
          )}
        </AnimatePresence>
      </main>

      <footer style={{ padding: '10px 25px', fontSize: '10px', color: '#555', display: 'flex', justifyContent: 'space-between', borderTop: '1px solid rgba(255,255,255,0.02)' }}>
        <span>ORACLE VERSION 2.1.0</span>
        <span>STARS ARE ALIGNED</span>
      </footer>
    </div>
  );
}

export default App;
