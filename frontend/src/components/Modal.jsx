import { useEffect } from "react";

// Reusable popup: dark background + white panel with a title bar.
// Closes on Escape, on the ✕ button, or when clicking the dark background.
// `wide` makes a large panel (used for document previews).
function Modal({ title, onClose, actions, wide = false, children }) {
  useEffect(() => {
    function handleKey(event) {
      if (event.key === "Escape") onClose();
    }
    document.addEventListener("keydown", handleKey);
    return () => document.removeEventListener("keydown", handleKey);
  }, [onClose]);

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div
        className={`modal-panel ${wide ? "modal-wide" : ""}`}
        role="dialog"
        aria-modal="true"
        aria-label={title}
        onClick={(event) => event.stopPropagation()} // clicks inside the panel don't close it
      >
        <div className="modal-header">
          <span className="modal-title">{title}</span>
          <div className="modal-actions">
            {actions}
            <button
              type="button"
              className="icon-button"
              aria-label="Close"
              title="Close"
              onClick={onClose}
            >
              ✕
            </button>
          </div>
        </div>
        <div className="modal-body">{children}</div>
      </div>
    </div>
  );
}

export default Modal;
