function ScaleIcon() {
  return (
    <svg
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M12 3v18M7 21h10M5 7h14M12 5l-7 2M12 5l7 2" />
      <path d="M5 7l-3 7a3.5 3.5 0 0 0 6 0L5 7zM19 7l-3 7a3.5 3.5 0 0 0 6 0l-3-7z" />
    </svg>
  );
}

function Logo() {
  return (
    <div className="logo">
      <span className="logo-icon">
        <ScaleIcon />
      </span>
      LexFlow
    </div>
  );
}

export default Logo;
