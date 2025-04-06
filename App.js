import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FilePlus, AlertTriangle } from 'lucide-react';

const PatientHealthAssistant = () => {
  const [formData, setFormData] = useState({
    age: 45,
    sex: 'Male',
    height: 175,
    weight: 85,
    allergies: '',
    preexisting_conditions: '',
    medications: '',
    family_history: '',
    question: '',
  });
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const API_BASE_URL = 'http://127.0.0.1:8000';

  const handleChange = useCallback((e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  }, []);

  const handleFileChange = useCallback((e) => {
    if (e.target.files) {
      setUploadedFiles(Array.from(e.target.files));
    }
  }, []);

  const handleSubmit = useCallback(async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResponse(null);

    const payload = new FormData();
    for (const key in formData) {
      payload.append(key, formData[key]);
    }
    uploadedFiles.forEach(file => {
      payload.append('files', file);
    });

    try {
      const res = await fetch(`${API_BASE_URL}/process-patient-data/`, {
        method: 'POST',
        body: payload,
      });

      if (!res.ok) {
        const errText = await res.text();
        throw new Error(errText || 'Request failed');
      }

      const data = await res.json();
      console.log("RESPONSE FROM BACKEND:", data);
      setResponse(data.insights);
    } catch (err) {
      setError(err.message || 'Something went wrong.');
    } finally {
      setLoading(false);
    }
  }, [formData, uploadedFiles]);

  return (
    <div style={{ backgroundColor: '#fff', minHeight: '100vh', padding: '2rem' }}>
      <div style={{ maxWidth: '900px', margin: '0 auto' }}>
        <h1 style={{ fontSize: '2.5rem', textAlign: 'center', marginBottom: '2rem', color: '#111' }}>
          Patient Health Assistant
        </h1>

        <form onSubmit={handleSubmit} style={{ background: '#f9f9f9', padding: '2rem', borderRadius: '1rem', boxShadow: '0 0 12px rgba(0,0,0,0.1)' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <input type="number" name="age" placeholder="Age" value={formData.age} onChange={handleChange} style={inputStyle} />
            <select name="sex" value={formData.sex} onChange={handleChange} style={inputStyle}>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
              <option value="Other">Other</option>
            </select>
            <input type="number" name="height" placeholder="Height (cm)" value={formData.height} onChange={handleChange} style={inputStyle} />
            <input type="number" name="weight" placeholder="Weight (kg)" value={formData.weight} onChange={handleChange} style={inputStyle} />
          </div>

          {["allergies", "preexisting_conditions", "medications", "family_history", "question"].map((field) => (
            <textarea
              key={field}
              name={field}
              placeholder={field.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}
              value={formData[field]}
              onChange={handleChange}
              rows={field === 'question' ? 4 : 2}
              style={{ ...inputStyle, marginTop: '1rem', width: '100%' }}
            />
          ))}

          <div style={{ marginTop: '1rem' }}>
            <label htmlFor="files" style={{ fontWeight: 'bold', color: '#333' }}>Upload Files:</label>
            <input type="file" id="files" multiple onChange={handleFileChange} accept=".pdf,.docx" style={{ display: 'block', marginTop: '0.5rem' }} />
            <ul>
              {uploadedFiles.map((file, idx) => <li key={idx} style={{ fontSize: '0.9rem', color: '#444' }}>{file.name}</li>)}
            </ul>
          </div>

          <button type="submit" disabled={loading} style={submitStyle}>
            {loading ? 'Processing...' : 'Submit'}
          </button>
        </form>

        {response && (
          <div style={{ marginTop: '2rem', backgroundColor: '#eef6ff', padding: '1.5rem', borderRadius: '1rem', color: '#111' }}>
            <h2 style={{ color: '#2563eb', marginBottom: '1rem' }}>Health Insights</h2>
            <p style={{ whiteSpace: 'pre-wrap' }}>{response}</p>
          </div>
        )}

        {error && (
          <div style={{ marginTop: '2rem', backgroundColor: '#fee2e2', padding: '1.5rem', borderRadius: '1rem', color: '#b91c1c' }}>
            <strong>Error:</strong> {error}
          </div>
        )}
      </div>
    </div>
  );
};

const inputStyle = {
  padding: '0.75rem',
  borderRadius: '0.5rem',
  border: '1px solid #ccc',
  width: '100%',
  fontSize: '1rem',
  color: '#111'
};

const submitStyle = {
  marginTop: '2rem',
  backgroundColor: '#2563eb',
  color: 'white',
  padding: '0.75rem 2rem',
  fontSize: '1rem',
  borderRadius: '0.5rem',
  border: 'none',
  cursor: 'pointer'
};

export default PatientHealthAssistant;