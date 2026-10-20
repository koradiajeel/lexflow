// Build-time switches (set by the GitHub Pages workflow, not used for local development).

// The public demo on GitHub Pages has no backend yet, so it shows only the landing page:
// no Sign in / Register, and every other address goes back to "/".
export const IS_DEMO = import.meta.env.VITE_DEMO_MODE === "true";

export const GITHUB_URL = "https://github.com/koradiajeel/lexflow";
