import React, { useState } from 'react';
import './App.css';

function App() {
  const [resumeFiles, setResumeFiles] = useState([]);  // <-- updated
  const [job, setJob] = useState('');
  const [results, setResults] = useState([]); // <-- updated
  const [loading, setLoading] = useState(false);
  const [useLLM, setUseLLM] = useState(false);
  const [apiKey, setApiKey] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (resumeFiles.length === 0 || !job) {
      alert('Please upload at least one resume and enter job description.');
      return;
    }

    const formData = new FormData();
    resumeFiles.forEach((file, index) => {
      formData.append('resumes', file); // backend will expect 'resumes'
    });
    formData.append('job', job);
    
    if (useLLM) {
      if (!apiKey) {
        alert('Please enter your OpenAI API key.');
        return;
      }
      formData.append('api_key', apiKey);
    }

    setLoading(true);

    try {
      const endpoint = useLLM
      ? 'http://localhost:5000/api/match_llm'
      : 'http://localhost:5000/api/match';
      
      const response = await fetch(endpoint, {
        method: 'POST',
        body: formData
      });

      const data = await response.json();
      console.log("Backend response:", data);
      setResults(data.results); // assume array of matches
    } catch (error) {
      alert('Error uploading. Make sure Flask API is running.');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };
  
  const handleDownloadTopResumes = async () => {
    const formData = new FormData();

    
    // Get names of resumes that scored >= 0.5
    const topFilenames = results
      .filter((res) => res.score >= 0.5)
      .map((res) => res.filename);
    
    // Match and append only those resume files
    resumeFiles.forEach((file) => {
      if (topFilenames.includes(file.name)) {
        formData.append('resumes', file);
      }
    });

    try {
      const response = await fetch('http://localhost:5000/api/download-top', {
        method: 'POST',
        body: formData
      });

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'top_candidates.zip';
      a.click();
      a.remove();
    } catch (err) {
      console.error('Download failed:', err);
      alert('Download failed. See console for details.');
    }
  };



  return (
    <div className="app-container">
      <header className="header">
        <h1>🔍 Resume Parser & Job Fit Analyzer</h1>
        <p>Upload one or more resumes and match them with a job description</p>
      </header>

      <main className="form-area">
        <form onSubmit={handleSubmit} className="match-form" encType="multipart/form-data">
          <label className="upload-label">
            Upload Resumes (PDFs)
            <input
              type="file"
              accept=".pdf"
              multiple
              onChange={(e) => setResumeFiles(Array.from(e.target.files))}
              className="file-input"
            />
          </label>

          <textarea
            placeholder="Paste Job Description Here..."
            value={job}
            onChange={(e) => setJob(e.target.value)}
            className="input-area"
          />

          <button type="submit" className="submit-btn" disabled={loading}>
            {loading ? 'Analyzing...' : 'Check Match'}
          </button>
        </form>
        <div className="llm-toggle-section">
          <label>
            <input
              type="checkbox"
              checked={useLLM}
              onChange={(e) => setUseLLM(e.target.checked)}
            />
            🔮 Use OpenAI LLM for enhanced accuracy
          </label>

          {useLLM && (
            <input
              type="password"
              placeholder="Enter your OpenAI API key"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              className="api-key-input"
            />
          )}
        </div>

        {Array.isArray(results) && results.length > 0 && (
          <div className="results-section">
            <h3>Top Matching Resumes</h3>
            <ul>
              {results.map((res, index) => (
                <li key={index}>
                  <strong>{res.candidateName}</strong>- {res.filename} 
                  {/* <strong>{res.candidateName}</strong>- {res.filename} - Match Score: {res.score}% */}
                </li>
                
              ))}
              
            </ul>
            <button onClick={handleDownloadTopResumes} className="submit-btn2">
                    📦 Download Top Resumes
            </button>
          </div>
        )}

      </main>

      <footer className="footer">
        <p>© 2025 Resume Parser & Job Fit Analyzer | Hasnain Tariq</p>
      </footer>
    </div>
  );
}

export default App;