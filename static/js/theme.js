/**
 * Theme toggle for SaveCircle.
 *
 * Persists the chosen theme in localStorage and falls back to the
 * visitor's OS preference on first visit. The inline snippet in
 * base.html applies the stored theme before paint to avoid a flash of
 * the wrong theme; this file just wires up the toggle button.
 */
(function () {
  "use strict";

  const STORAGE_KEY = "savecircle-theme";

  function getStoredTheme() {
    return localStorage.getItem(STORAGE_KEY);
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem(STORAGE_KEY, theme);
  }

  document.addEventListener("DOMContentLoaded", function () {
    const toggle = document.querySelector("[data-theme-toggle]");
    if (!toggle) {
      return;
    }

    toggle.addEventListener("click", function () {
      const current = document.documentElement.getAttribute("data-theme") === "dark" ? "dark" : "light";
      const next = current === "dark" ? "light" : "dark";
      applyTheme(next);
    });
  });
})();