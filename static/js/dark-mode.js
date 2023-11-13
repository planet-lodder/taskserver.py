let get = (id) => document.getElementById(id);
let stored = (k) => localStorage.getItem(k);
let stores = (k, v) => localStorage.setItem(k, v);

// Set tailwid darkmode to be driven off a classname
if (tailwind) tailwind.config = { darkMode: "class" };
if (isDarkMode()) document.body.classList.add("dark");

function isDarkMode() {
  let hasLocal = "color-theme" in localStorage;
  let localValue = hasLocal && stored("color-theme");
  let mediaDark = "(prefers-color-scheme: dark)";

  // Try and determine the current prefference
  if (hasLocal && localValue === "dark") return true;
  if (!hasLocal && window.matchMedia(mediaDark).matches) return true;
  return false;
}

function initDarkMode() {
  // Get refferences to dark mode toggle buttons
  let target = document.body;
  let themeToggleDarkIcon = get("theme-toggle-dark-icon");
  let themeToggleLightIcon = get("theme-toggle-light-icon");

  // Try and determine the current prefference
  let isDark = isDarkMode();

  // Change the icons inside the button based on previous settings
  if (isDark) {
    themeToggleLightIcon && themeToggleLightIcon.classList.remove("hidden");
    target.classList.add("dark");
  } else {
    themeToggleDarkIcon && themeToggleDarkIcon.classList.remove("hidden");
    target.classList.remove("dark");
  }
}

function bindDarkModeButton() {
  let themeToggleBtn = get("theme-toggle");
  if (themeToggleBtn) {
    themeToggleBtn.addEventListener("click", toggleDarkMode);
  }
}

function toggleDarkMode() {
  let target = document.body;
  let themeToggleDarkIcon = get("theme-toggle-dark-icon");
  let themeToggleLightIcon = get("theme-toggle-light-icon");

  // toggle icons inside button
  themeToggleDarkIcon && themeToggleDarkIcon.classList.toggle("hidden");
  themeToggleLightIcon && themeToggleLightIcon.classList.toggle("hidden");

  // if set via local storage previously
  var value = stored("color-theme");
  if (value == "light" || !target.classList.contains("dark")) {
    target.classList.add("dark");
    stores("color-theme", "dark");
  } else {
    target.classList.remove("dark");
    stores("color-theme", "light");
  }
}

// Bind dark mode as soon as possible
addEventListener("DOMContentLoaded", (event) => initDarkMode());

// Set dark mode toggle only when page has loaded
addEventListener("load", (event) => bindDarkModeButton());
