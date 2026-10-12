import Modal from "./Modal";

// Popup that shows a PDF or image inside the page.
// `url` is a temporary in-memory link to the file (made with URL.createObjectURL).
function DocumentPreview({ doc, url, onClose, onDownload }) {
  const isImage = doc.content_type.startsWith("image/");

  return (
    <Modal
      title={doc.filename}
      onClose={onClose}
      wide
      actions={
        <button type="button" className="btn btn-outline btn-sm" onClick={onDownload}>
          Download
        </button>
      }
    >
      {isImage ? (
        <img src={url} alt={doc.filename} className="preview-image" />
      ) : (
        <iframe src={url} title={doc.filename} className="preview-frame" />
      )}
    </Modal>
  );
}

export default DocumentPreview;
