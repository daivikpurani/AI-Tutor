import React, { useEffect, useState } from 'react';
import { fetchSections, uploadMaterial, fetchMaterialsForSection } from './api';

export default function PVMaterials() {
  const [sections, setSections] = useState([]);
  const [sectionId, setSectionId] = useState('');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [materials, setMaterials] = useState([]);

  useEffect(() => {
    fetchSections()
      .then((s) => { setSections(s); if (s.length) setSectionId(String(s[0].id)); })
      .catch(() => setSections([]));
  }, []);

  useEffect(() => {
    if (!sectionId) return;
    fetchMaterialsForSection(Number(sectionId))
      .then(setMaterials)
      .catch(() => setMaterials([]));
  }, [sectionId]);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    if (!file || !sectionId || !title.trim()) {
      setError('Select a section, enter a title, and choose a PDF.');
      return;
    }
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setError('Only PDF files are supported.');
      return;
    }
    setLoading(true);
    try {
      await uploadMaterial(Number(sectionId), title.trim(), file, description.trim() || undefined);
      setSuccess('Material uploaded and indexed into vector store.');
      setTitle('');
      setDescription('');
      setFile(null);
      e.target.reset();
      fetchMaterialsForSection(Number(sectionId)).then(setMaterials).catch(() => {});
    } catch (err) {
      setError(err.message || 'Upload failed.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <p className="g-page-title">Upload course materials</p>
      <p className="g-page-subtitle">
        Select a course section, then upload a PDF. It will be chunked and indexed into the vector store used for AI grading.
      </p>

      <div className="g-card">
        <h3>New material</h3>
        <form onSubmit={handleSubmit}>
          <div className="g-form-row">
            <label>Section</label>
            <select value={sectionId} onChange={(e) => setSectionId(e.target.value)} required>
              <option value="">Select section…</option>
              {sections.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.section_code}{s.course_name ? ` — ${s.course_name}` : ''}
                </option>
              ))}
            </select>
          </div>
          <div className="g-form-row">
            <label>Title</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Week 1 Lecture Notes"
              required
            />
          </div>
          <div className="g-form-row">
            <label>Description (optional)</label>
            <input
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Brief description of the material"
            />
          </div>
          <div className="g-form-row">
            <label>PDF file</label>
            <input
              type="file"
              accept=".pdf"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              required
            />
          </div>

          {error   && <div className="g-status-err">{error}</div>}
          {success && <div className="g-status-ok">{success}</div>}

          <div className="g-btn-row">
            <button type="submit" className="g-btn" disabled={loading}>
              {loading ? 'Uploading…' : 'Upload material'}
            </button>
          </div>
        </form>
      </div>

      <div className="g-card">
        <h3>Materials for selected section</h3>
        {materials.length === 0 ? (
          <p className="g-empty">No materials uploaded yet.</p>
        ) : (
          <ul className="g-list">
            {materials.map((m) => (
              <li key={m.id}>
                <strong>{m.title}</strong>
                <span className="meta"> — {m.file_name}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </>
  );
}
