import React, { useState } from 'react';
import axios from 'axios';
import Plotly from 'plotly.js';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

function App() {
  const [geneInput, setGeneInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [results, setResults] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResults(null);

    try {
      // Parse gene input (split by whitespace, comma, or newline)
      const genes = geneInput
        .split(/[\s,]+/)
        .map(g => g.trim())
        .filter(g => g.length > 0);

      if (genes.length === 0) {
        setError('Please enter at least one gene symbol');
        setLoading(false);
        return;
      }

      // Send request to backend
      const response = await axios.post('/api/process-genes', { genes });
      
      if (response.data.success) {
        setResults(response.data);
      } else {
        setError(response.data.error || 'Failed to process genes');
      }
    } catch (err) {
      console.error('Error:', err);
      setError('Failed to connect to server. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  const renderHeatmap = (data, title) => {
    if (!data || !data.data || data.data.length === 0) {
      return <div>No data available for {title}</div>;
    }

    const heatmapData = [{
      z: data.data,
      x: data.samples,
      y: data.genes,
      type: 'heatmap',
      colorscale: 'RdBu',
      reversescale: true,
      colorbar: { title: 'Z-score' }
    }];

    const layout = {
      title: title,
      width: 800,
      height: Math.max(400, data.genes.length * 20),
      margin: { t: 50, b: 150, l: 150, r: 50 },
      xaxis: { 
        tickangle: -45,
        automargin: true
      },
      yaxis: { 
        automargin: true,
        tickfont: { size: 12 }
      }
    };

    return (
      <div className="heatmap-container">
        <div id={`heatmap-${title.replace(/\s+/g, '-')}`}></div>
      </div>
    );
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Gene Expression Heatmap Clustering</h1>
        <p>Visualize gene expression patterns across development time and tissues</p>
      </header>

      <main className="container mt-4">
        <form onSubmit={handleSubmit}>
          <div className="mb-3">
            <label htmlFor="geneInput" className="form-label">
              Enter Gene Symbols (one per line, or separated by commas/spaces):
            </label>
            <textarea
              id="geneInput"
              className="form-control"
              rows="5"
              value={geneInput}
              onChange={(e) => setGeneInput(e.target.value)}
              placeholder="TP53&#10;BRCA1&#10;MYC&#10;EGFR&#10;KRAS"
            />
          </div>
          <button 
            type="submit" 
            className="btn btn-primary"
            disabled={loading}
          >
            {loading ? 'Processing...' : 'Generate Heatmaps'}
          </button>
        </form>

        {error && (
          <div className="alert alert-danger mt-3" role="alert">
            {error}
          </div>
        )}

        {results && (
          <div className="results mt-4">
            {results.invalid_genes && results.invalid_genes.length > 0 && (
              <div className="alert alert-warning">
                Warning: The following genes were not found in our datasets: {results.invalid_genes.join(', ')}
              </div>
            )}

            <div className="row">
              <div className="col-12 mb-4">
                <h2>BrainSpan Developmental Transcriptome</h2>
                {renderHeatmap(results.brainspan, 'Development Time')}
              </div>
              <div className="col-12">
                <h2>GTEx Tissue Expression</h2>
                {renderHeatmap(results.gtex, 'Tissue Types')}
              </div>
            </div>
          </div>
        )}
      </main>

      <footer className="App-footer mt-5 p-3 bg-light">
        <p>Data sources: <a href="https://www.brainspan.org/" target="_blank" rel="noopener noreferrer">BrainSpan</a> | <a href="https://gtexportal.org/" target="_blank" rel="noopener noreferrer">GTEx</a></p>
      </footer>
    </div>
  );
}

export default App;