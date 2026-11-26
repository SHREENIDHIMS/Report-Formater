const modes = [
  {
    number: "01",
    title: "Automatic",
    description:
      "Upload an existing Word report. Review detected sections and formatting changes before applying them.",
    tag: "I already have a DOCX",
  },
  {
    number: "02",
    title: "Manual",
    description:
      "Start with a guided report outline. Add chapters, tables, figures and references in a structured editor.",
    tag: "Start from scratch",
  },
  {
    number: "03",
    title: "Hybrid",
    description:
      "Import your report, apply safe formatting fixes, then edit and complete it in the browser.",
    tag: "Format + continue editing",
  },
];

const benefits = [
  ["Format-aware", "Work against a selected, versioned VTU template—not a generic Word theme."],
  ["Editable output", "Keep an editable DOCX and a rendered PDF for printing or submission."],
  ["Visible checks", "See what passed, what needs review and which rule each finding came from."],
];

export default function Home() {
  return (
    <main>
      <header className="topbar shell">
        <a className="brand" href="#top" aria-label="VTU Report Studio home">
          <span className="brand-mark">R</span>
          <span>report<span className="brand-light">studio</span></span>
        </a>
        <nav className="nav-links" aria-label="Main navigation">
          <a href="#how-it-works">How it works</a>
          <a href="#modes">Workflows</a>
          <a href="#trust">Why Report Studio</a>
        </nav>
        <a className="nav-cta" href="#start">Get started <span aria-hidden="true">↗</span></a>
      </header>

      <section className="hero shell" id="top">
        <div className="hero-copy">
          <div className="eyebrow"><span className="eyebrow-dot" /> BUILT FOR VTU PROJECT REPORTS</div>
          <h1>Your project.<br /><em>Your format.</em><br />Less time fixing Word.</h1>
          <p className="hero-lede">
            Create a report from scratch or bring the one you already wrote.
            Apply a selected VTU format, review the changes and export an
            editable Word document plus PDF.
          </p>
          <div className="hero-actions" id="start">
            <a className="button-primary" href="#modes">Start your report <span aria-hidden="true">→</span></a>
            <a className="button-quiet" href="#how-it-works">See how it works</a>
          </div>
          <div className="hero-note"><span className="note-check">✓</span> Student-first · No college account required</div>
        </div>

        <div className="preview-wrap" aria-label="Illustrative report preview">
          <div className="preview-orbit orbit-one" />
          <div className="preview-orbit orbit-two" />
          <div className="floating-chip chip-top"><span className="chip-icon">✓</span> Rules checked</div>
          <div className="document-card">
            <div className="doc-topline"><span>PROJECT REPORT</span><span>2026</span></div>
            <div className="doc-university">VISVESVARAYA TECHNOLOGICAL UNIVERSITY</div>
            <div className="doc-rule" />
            <div className="doc-small">A PROJECT REPORT ON</div>
            <div className="doc-title">Smart Campus<br />Management System</div>
            <div className="doc-subtitle">Submitted in partial fulfilment of the requirements</div>
            <div className="doc-divider" />
            <div className="doc-columns">
              <div><span className="doc-label">Submitted by</span><b>Student Name</b><small>USN: 4XX22CS000</small></div>
              <div><span className="doc-label">Under the guidance of</span><b>Guide Name</b><small>Assistant Professor</small></div>
            </div>
            <div className="doc-footer"><span>Department of CSE</span><span>2025–26</span></div>
          </div>
          <div className="floating-chip chip-bottom"><span className="chip-file">DOCX</span> Editable export</div>
        </div>
      </section>

      <section className="trust-strip shell" id="trust">
        <span>ONE WORKSPACE FOR THE FINAL FORMATTING WORK</span>
        <div className="trust-items"><b>Import</b><i /> <b>Format</b><i /> <b>Review</b><i /> <b>Export</b></div>
      </section>

      <section className="section shell" id="modes">
        <div className="section-heading">
          <div><div className="eyebrow">THREE WAYS TO GET STARTED</div><h2>Start wherever<br /><em>your report is.</em></h2></div>
          <p>Already have a 60-page Word file? Start with it. Haven’t written anything yet? Build it section by section.</p>
        </div>
        <div className="mode-grid">
          {modes.map((mode) => (
            <article className="mode-card" key={mode.number}>
              <div className="mode-number">{mode.number}</div>
              <div className="mode-tag">{mode.tag}</div>
              <h3>{mode.title}</h3>
              <p>{mode.description}</p>
              <a href="#how-it-works" aria-label={`Learn about ${mode.title} mode`}>Explore workflow <span aria-hidden="true">↗</span></a>
            </article>
          ))}
        </div>
      </section>

      <section className="process-band" id="how-it-works">
        <div className="shell process-inner">
          <div><div className="eyebrow eyebrow-light">A CLEARER WAY TO FINISH</div><h2>From working draft<br />to <em>submission-ready.</em></h2></div>
          <div className="process-steps">
            <div><span>01</span><b>Choose a format</b><small>Select an available VTU template version for your course and cohort.</small></div>
            <div><span>02</span><b>Build or upload</b><small>Start manually, import DOCX, or combine both workflows.</small></div>
            <div><span>03</span><b>Review and export</b><small>Inspect formatting findings and export DOCX plus PDF.</small></div>
          </div>
        </div>
      </section>

      <section className="section shell feature-section">
        <div className="section-heading"><div><div className="eyebrow">MADE FOR THE DETAILS</div><h2>Formatting should be<br /><em>the easy part.</em></h2></div><p>Keep the rules visible, the original document safe and the final export editable.</p></div>
        <div className="benefit-grid">
          {benefits.map(([title, text], index) => <div className="benefit" key={title}><span>0{index + 1}</span><h3>{title}</h3><p>{text}</p></div>)}
        </div>
      </section>

      <footer className="footer shell">
        <a className="brand" href="#top"><span className="brand-mark">R</span><span>report<span className="brand-light">studio</span></span></a>
        <p>Independent student tool. Template applicability must be checked against the selected scheme and college instructions.</p>
        <span>© {new Date().getFullYear()} VTU Report Studio · Working name</span>
      </footer>
    </main>
  );
}
