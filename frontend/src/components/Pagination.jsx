// Previous / "Page N" / Next. Hidden when everything fits on page 1.
function Pagination({ page, hasNext, onChange }) {
  if (page === 1 && !hasNext) return null;

  return (
    <div className="pagination">
      <button
        type="button"
        className="btn btn-outline btn-sm"
        disabled={page === 1}
        onClick={() => onChange(page - 1)}
      >
        Previous
      </button>
      <span className="pagination-label">Page {page}</span>
      <button
        type="button"
        className="btn btn-outline btn-sm"
        disabled={!hasNext}
        onClick={() => onChange(page + 1)}
      >
        Next
      </button>
    </div>
  );
}

export default Pagination;
