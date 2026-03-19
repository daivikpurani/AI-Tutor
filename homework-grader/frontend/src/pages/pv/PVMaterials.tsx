import React, { useEffect, useState } from 'react';
import { fetchSections, uploadMaterial, fetchMaterialsForSection } from '../../api';

export default function PVMaterials() {
  const [sections, setSections] = useState<{ id: number; section_code: string; course_name: string | null }[]>([]);
  const [sectionId, setSectionId] = useState('');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [materials, setMaterials] = useState<{ id: number; title: string; file_name: string }[]>([]);

  useEffect(() => {
    fetchSections().then((s) => {
      setSections(s);
      if (s.length && !sectionId) setSectionId(String(s[0].id));
    }).catch(() => setSections([]));
  }, []);

  useEffect(() => {
    if (!sectionId) return;
    fetchMaterialsForSection(Number(sectionId))
      .then((d) => setMaterials(d.materials ?? []))
      .catch(() => setMaterials([]));
  }, [sectionId]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    if (!file || !sectionId || !title.trim()) {
      setError('Select section, enter title, and choose a PDF.');
      return;
    }
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setError('Only PDF files supported.');
      return;
    }
    setLoading(true);
    try {
      await uploadMaterial(Number(sectionId), title.trim(), file, description.trim() || undefined);
      setSuccess('Material uploaded and indexed.');
      setTitle('');
      setDescription('');
      setFile(null);
      const d = await fetchMaterialsForSection(Number(sectionId));
      setMaterials(d.materials ?? []);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Upload failed');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="pv-materials">
      <h2>Upload course materials</h2>
      <p>Select course/section, then upload a PDF. It will be chunked and indexed for AI grading.</p>

      <div className="card form-card">
        <form onSubmit={handleSubmit}>
          <div className="form-row">
            <label>Section</label>
            <select value={sectionId} onChange={(e) => setSectionId(e.target.value)} required>
              <option value="">Select section</option>
              {sections.map((s) => (
                <option key={s.id} value={s.id}>{s.section_code} — {s.course_name}</option>
              ))}
            </select>
          </div>
          <div className="form-row">
            <label>Title</label>
            <input type="text" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="e.g. Week 1 Notes" required />
          </div>
          <div className="form-row">
            <label>Description (optional)</label>
            <input type="text" value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Brief description" />
          </div>
          <div className="form-row">
            <label>PDF file</label>
            <input type="file" accept=".pdf" onChange={(e) => setFile(e.target.files?.[0] ?? null)} required />
          </div>
          {error && <p className="status-err">{error}</p>}
          {success && <p className="status-ok">{success}</p>}
          <button type="submit" className="btn" disabled={loading}>{loading ? 'Uploading…' : 'Upload material'}</button>
        </form>
      </div>

      <div className="card">
        <h3>Materials for selected section</h3>
        {materials.length === 0 ? <p>No materials yet.</p> : (
          <ul className="list">
            {materials.map((m) => (
              <li key={m.id}><strong>{m.title}</strong> — {m.file_name}</li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
