const storageKey = "theme";
const root = document.documentElement;

function readStoredTheme() {
  try {
    return localStorage.getItem(storageKey);
  } catch {
    return null;
  }
}

function storeTheme(value) {
  try {
    localStorage.setItem(storageKey, value);
  } catch {
    return;
  }
}

function applyTheme(value) {
  if (value) root.dataset.theme = value;
}

function currentTheme() {
  if (root.dataset.theme) return root.dataset.theme;
  return matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

applyTheme(readStoredTheme());

document.getElementById("theme").addEventListener("click", () => {
  const next = currentTheme() === "dark" ? "light" : "dark";
  applyTheme(next);
  storeTheme(next);
});

const chips = document.querySelectorAll(".chip");
const cards = document.querySelectorAll(".card");

function showType(type) {
  cards.forEach((card) => {
    card.hidden = type !== "all" && card.dataset.type !== type;
  });
  chips.forEach((chip) => chip.setAttribute("aria-pressed", String(chip.dataset.filter === type)));
}

chips.forEach((chip) => chip.addEventListener("click", () => showType(chip.dataset.filter)));
