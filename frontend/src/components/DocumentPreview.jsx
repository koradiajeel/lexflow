import { useEffect } from "react";

// Popup that shows a PDF or image inside the page.
// `url` is a temporary in-memory link to the file (made with URL.createObjectURL).
function DocumentPreview({ doc, url, onClose, onDownload }) {
  // Close with the Escape key.
  useEffect(() => {
    function handleKey(event) {
      if (event.key === "Escape") onClose();
    }
    document.addEventListener("keydown", handleKey);
    return () => document.removeEventListener("keydown", handleKey);
  }, [onClose]);

  const isImage = doc.content_type.startsWith("image/");

  return (
    // Clicking the dark background closes the popup; clicks inside the panel don't.
    <div className="preview-backdrop" onClick={onClose}>
      <div
        className="preview-panel"
        role="dialog"
        aria-modal="true"
        aria-label={`Preview of ${doc.filename}`}
        onClick={(event) => event.stopPropagation()}
      >
        <div className="preview-header">
          <span className="preview-title">{doc.filename}</span>
          <div className="preview-actions">
            <button type="button" className="btn btn-outline btn-sm" onClick={onDownload}>
              Download
            </button>
            <button
              type="button"
              className="icon-button"
              aria-label="Close preview"
              title="Close"
              onClick={onClose}
            >
              ✕
            </button>
          </div>
        </div>

        <div className="preview-body">
          {isImage ? (
            <img src={url} alt={doc.filename} className="preview-image" />
          ) : (
            <iframe src={url} title={doc.filename} className="preview-frame" />
          )}
        </div>
      </div>
    </div>
  );
}

export default DocumentPreview;
