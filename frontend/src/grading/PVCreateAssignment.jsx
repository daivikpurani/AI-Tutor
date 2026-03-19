import React, { useEffect, useRef, useState } from 'react';
import { fetchSections, createAssignment, extractQuestionsFromPdf } from './api';

export default function PVCreateAssignment() {
  const [sections, setSections] = useState([]);
  const [sectionId, setSectionId] = useState('');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [questionsContent, setQuestionsContent] = useState('');
  const [questionsFileName, setQuestionsFileName] = useState(null);
  const [questionsExtracting, setQuestionsExtracting] = useState(false);
  const [gradingInstructions, setGradingInstructions] = useState('');
  const [maxScore, setMaxScore] = useState(100);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const pdfRef = useRef(null);

  useEffect(() => {
    fetchSections()
      .then((s) => { setSections(s); if (s.length) setSectionId(String(s[0].id)); })
      .catch(() => setSections([]));
  }, []);

  async function handleQuestionsPdf(e) {
    const f = e.target.files?.[0];
    if (!f) return;
    if (!f.name.toLowerCase().endsWith('.pdf')) { setError('Please upload a PDF.'); return; }
    setQuestionsExtracting(true);
    setError(null);
    try {
      const { text } = await extractQuestionsFromPdf(f);
      setQuestionsContent(text || '');
      setQuestionsFileName(f.name);
    } catch (err) {
      setError(err.message || 'Failed to extract PDF text.');
    } finally {
      setQuestionsExtracting(false);
      e.target.value = '';
    }
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    if (!sectionId || !title.trim()) { setError('Section and title are required.'); return; }
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
      setSuccess('Assignment created. Students can now see it.');
      setTitle('');
      setDescription('');
      setQuestionsContent('');
      setQuestionsFileName(null);
      setGradingInstructions('');
      setMaxScore(100);
    } catch (err) {
      setError(err.message || 'Failed to create assignment.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <p className="g-page-title">Create assignment</p>
      <p className="g-page-subtitle">
        Define a homework assignment for a section. Upload a questions PDF or paste them directly.
        AI grading instructions tell the model how to evaluate student submissions.
      </p>

      <div className="g-card">
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
              placeholder="e.g. Homework 1 — Data Structures"
              required
            />
          </div>

          <div className="g-form-row">
            <label>Description (optional)</label>
            <input
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Brief description"
            />
          </div>

          <div className="g-form-row">
            <label>Homework questions</label>
            <input
              ref={pdfRef}
              type="file"
              accept=".pdf"
              onChange={handleQuestionsPdf}
              style={{ display: 'none' }}
            />
            <div className="g-btn-row" style={{ marginTop: 0, marginBottom: '8px' }}>
              <button
                type="button"
                className="g-btn-ghost"
                onClick={() => pdfRef.current?.click()}
                disabled={questionsExtracting}
              >
                {questionsExtracting
                  ? 'Extracting…'
                  : questionsFileName
                  ? `Replace PDF (${questionsFileName})`
                  : 'Upload questions PDF'}
              </button>
            </div>
            {questionsFileName && !questionsExtracting && (
              <p className="g-extract-hint">Text extracted — edit below if needed.</p>
            )}
            <textarea
              value={questionsContent}
              onChange={(e) => setQuestionsContent(e.target.value)}
              placeholder="Paste questions here, or upload a PDF above. Students will see this."
              rows={6}
            />
          </div>

          <div className="g-form-row">
            <label>AI grading instructions (optional)</label>
            <textarea
              value={gradingInstructions}
              onChange={(e) => setGradingInstructions(e.target.value)}
              placeholder="e.g. Focus on correctness and code clarity. Award partial credit for…"
              rows={3}
            />
          </div>

          <div className="g-form-inline">
            <div className="g-form-row" style={{ flex: 1 }}>
              <label>Max score</label>
              <input
                type="number"
                min={1}
                value={maxScore}
                onChange={(e) => setMaxScore(Number(e.target.value))}
              />
            </div>
          </div>

          {error   && <div className="g-status-err">{error}</div>}
          {success && <div className="g-status-ok">{success}</div>}

          <div className="g-btn-row">
            <button type="submit" className="g-btn" disabled={loading}>
              {loading ? 'Creating…' : 'Create assignment'}
            </button>
          </div>
        </form>
      </div>
    </>
  );
}
