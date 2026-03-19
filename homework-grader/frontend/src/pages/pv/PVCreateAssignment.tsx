import React, { useEffect, useRef, useState } from 'react';
import { fetchSections, createAssignment, extractQuestionsFromPdf } from '../../api';

export default function PVCreateAssignment() {
  const [sections, setSections] = useState<{ id: number; section_code: string; course_name: string | null }[]>([]);
  const [sectionId, setSectionId] = useState('');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [questionsContent, setQuestionsContent] = useState('');
  const [questionsFileName, setQuestionsFileName] = useState<string | null>(null);
  const [questionsExtracting, setQuestionsExtracting] = useState(false);
  const questionsFileRef = useRef<HTMLInputElement>(null);
  const [gradingInstructions, setGradingInstructions] = useState('');
  const [maxScore, setMaxScore] = useState(100);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    fetchSections().then((s) => {
      setSections(s);
      if (s.length && !sectionId) setSectionId(String(s[0].id));
    }).catch(() => setSections([]));
  }, []);

  async function handleQuestionsPdfChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setError('Please upload a PDF file.');
      return;
    }
    setQuestionsExtracting(true);
    setError(null);
    try {
      const { text } = await extractQuestionsFromPdf(file);
      setQuestionsContent(text || '');
      setQuestionsFileName(file.name);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to extract PDF text');
    } finally {
      setQuestionsExtracting(false);
      e.target.value = '';
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    if (!sectionId || !title.trim()) {
      setError('Section and title are required.');
      return;
    }
    setLoading(true);
    try {
      await createAssignment({
        section_id: Number(sectionId),
        title: title.trim(),
        description: description.trim() || undefined,
        questions_content: questionsContent.trim() || undefined,
        grading_instructions: gradingInstructions.trim() || undefined,
        max_score: maxScore,
      });
      setSuccess('Assignment created. Students can see it now.');
      setTitle('');
      setDescription('');
      setQuestionsContent('');
      setQuestionsFileName(null);
      setGradingInstructions('');
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="pv-create-assignment">
      <h2>Create assignment</h2>
      <p>Select course/section and add homework details. Optional AI grading instructions help the AI grade based on materials + assignment.</p>

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
            <input type="text" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="e.g. Homework 1" required />
          </div>
          <div className="form-row">
            <label>Description (optional)</label>
            <input type="text" value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Brief description" />
          </div>
          <div className="form-row">
            <label>Homework questions (optional)</label>
            <div className="questions-upload-row">
              <input
                ref={questionsFileRef}
                type="file"
                accept=".pdf"
                onChange={handleQuestionsPdfChange}
                className="file-input"
                style={{ display: 'none' }}
              />
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => questionsFileRef.current?.click()}
                disabled={questionsExtracting}
              >
                {questionsExtracting ? 'Extracting…' : questionsFileName ? `Replace PDF (${questionsFileName})` : 'Upload PDF'}
              </button>
              {questionsFileName && !questionsExtracting && (
                <span className="file-name-hint">Text extracted below. Edit if needed.</span>
              )}
            </div>
            <textarea
              value={questionsContent}
              onChange={(e) => setQuestionsContent(e.target.value)}
              placeholder="Paste homework questions or upload a PDF above. Students will see this in the assignment view."
              rows={6}
            />
          </div>
          <div className="form-row">
            <label>AI grading instructions (optional)</label>
            <textarea
              value={gradingInstructions}
              onChange={(e) => setGradingInstructions(e.target.value)}
              placeholder="e.g. Focus on correctness and clarity. If left empty, AI grades from materials + homework context."
              rows={3}
            />
          </div>
          <div className="form-row inline">
            <div>
              <label>Max score</label>
              <input type="number" min={1} value={maxScore} onChange={(e) => setMaxScore(Number(e.target.value))} />
            </div>
          </div>
          {error && <p className="status-err">{error}</p>}
          {success && <p className="status-ok">{success}</p>}
          <button type="submit" className="btn" disabled={loading}>{loading ? 'Creating…' : 'Create assignment'}</button>
        </form>
      </div>
    </div>
  );
}
