export const COLOR_SCHEME_STORAGE_KEY = "fu-consultant-dark-mode";

// Older releases stored booleans under this key. MUI expects explicit mode names.
export const COLOR_SCHEME_MIGRATION_SCRIPT = `(function () {
  try {
    var key = ${JSON.stringify(COLOR_SCHEME_STORAGE_KEY)};
    var stored = window.localStorage.getItem(key);
    if (stored === "true") window.localStorage.setItem(key, "dark");
    if (stored === "false") window.localStorage.setItem(key, "light");
  } catch (_) {}
})();`;
