import { createI18n, resolveLocale, SUPPORTED_LOCALES } from "./i18n.js";

const LANG_STORAGE_KEY = "armond-viewer-lang";

const state = {
  data: null,
  rootId: "P-0001",
  generations: 4,
  visibleNodes: 0,
  zoom: 1,
  autoFit: true,
  selected: null,
  locale: "en",
  // Mobile "focus view": the person currently centred, and the back stack.
  focusId: "P-0001",
  focusHistory: [],
};

// Active translator; reassigned by setLocale. UI code calls t / tn / vocab.
let i18n = createI18n("en");
const t = (key, vars) => i18n.t(key, vars);
const tn = (key, n, vars) => i18n.tn(key, n, vars);
const vocab = (kind, value) => i18n.label(kind, value);
// Place names are stored in English (repo convention); localise the one country
// word that differs at display time. Idempotent (pt "Brasil" is left untouched).
const localePlace = (name) =>
  typeof name === "string" && state.locale === "pt-BR" ? name.replace(/\bBrazil\b/g, "Brasil") : name;

// Resolve bilingual research content (transcript, summary/abstract, notes) to the
// active locale. Accepts either a { en, pt } pair or two positional strings; when
// Portuguese is selected and a translation exists it is shown, otherwise the
// English base is the fallback. Keeps the PT/EN toggle switching the content, not
// just the UI chrome.
const localeText = (value, ptText) => {
  const en = value && typeof value === "object" ? value.en : value;
  const pt = value && typeof value === "object" ? value.pt : ptText;
  return state.locale === "pt-BR" && typeof pt === "string" && pt.trim() ? pt : en || "";
};

// Small, self-contained flag glyphs keyed by the recorded nationality. Inline SVG
// (not emoji) so they render identically on every platform and stay offline. They
// mark nationality as recorded — never inferred ethnic origin.
const FLAG_SVGS = {
  Brazilian:
    '<svg viewBox="0 0 20 14" role="img" aria-hidden="true">' +
    '<rect width="20" height="14" fill="#009c3b"/>' +
    '<polygon points="10,1.4 18.6,7 10,12.6 1.4,7" fill="#ffdf00"/>' +
    '<circle cx="10" cy="7" r="3.5" fill="#002776"/>' +
    '<path d="M6.7 6.4 Q10 8.5 13.3 6.4" fill="none" stroke="#fff" stroke-width="0.8"/>' +
    "</svg>",
  Portuguese:
    '<svg viewBox="0 0 21 14" role="img" aria-hidden="true">' +
    '<rect width="21" height="14" fill="#da291c"/>' +
    '<rect width="8.4" height="14" fill="#046a38"/>' +
    '<circle cx="8.4" cy="7" r="2.8" fill="none" stroke="#ffdf00" stroke-width="0.9"/>' +
    '<rect x="7.3" y="4.6" width="2.2" height="4.8" rx="0.5" fill="#fff" stroke="#da291c" stroke-width="0.5"/>' +
    "</svg>",
  Swiss:
    '<svg viewBox="0 0 14 14" role="img" aria-hidden="true">' +
    '<rect width="14" height="14" fill="#da291c"/>' +
    '<rect x="5.5" y="2" width="3" height="10" fill="#fff"/>' +
    '<rect x="2" y="5.5" width="10" height="3" fill="#fff"/>' +
    "</svg>",
};

function nationalityFlag(nationality) {
  const svg = nationality && FLAG_SVGS[nationality];
  if (!svg) return null;
  const span = document.createElement("span");
  span.className = "person-flag";
  span.title = nationality;
  span.setAttribute("role", "img");
  span.setAttribute("aria-label", nationality);
  span.innerHTML = svg; // trusted static constant, no interpolation
  return span;
}

// Overview-cell value for the recorded nationality: the label plus the flag
// glyph when one exists. Returns a Node, or the "not established" text.
function nationalityValue(nationality) {
  if (!nationality) return t("value.notEstablished");
  const span = document.createElement("span");
  span.className = "fact-nationality";
  span.append(nationality);
  const flag = nationalityFlag(nationality);
  if (flag) span.append(flag);
  return span;
}

const MIN_ZOOM = 0.2;
const MAX_ZOOM = 2.5;
const FIT_MAX_ZOOM = 1.4;
const clamp = (value, min, max) => Math.min(max, Math.max(min, value));

let panState = null;
let suppressClick = false;
let lastFocused = null;

const elements = {
  rootSelect: document.querySelector("#root-person"),
  generationLimit: document.querySelector("#generation-limit"),
  search: document.querySelector("#person-search"),
  searchResults: document.querySelector("#search-results"),
  reset: document.querySelector("#reset-view"),
  loading: document.querySelector("#loading"),
  error: document.querySelector("#error"),
  tree: document.querySelector("#tree"),
  treeShell: document.querySelector(".tree-shell"),
  mobileView: document.querySelector("#mobile-view"),
  treeViewport: document.querySelector("#tree-viewport"),
  treeSizer: document.querySelector("#tree-sizer"),
  treeStage: document.querySelector("#tree-stage"),
  treeControls: document.querySelector("#tree-controls"),
  zoomIn: document.querySelector("#zoom-in"),
  zoomOut: document.querySelector("#zoom-out"),
  zoomFit: document.querySelector("#zoom-fit"),
  zoomLevel: document.querySelector("#zoom-level"),
  personCount: document.querySelector("#person-count"),
  familyCount: document.querySelector("#family-count"),
  sourceCount: document.querySelector("#source-count"),
  visibleCount: document.querySelector("#visible-count"),
  detailsPanel: document.querySelector("#details-panel"),
  backdrop: document.querySelector("#panel-backdrop"),
  closeDetails: document.querySelector("#close-details"),
  detailsId: document.querySelector("#details-id"),
  detailsTitle: document.querySelector("#details-title"),
  detailsLifespan: document.querySelector("#details-lifespan"),
  detailsContent: document.querySelector("#details-content"),
  languageSelect: document.querySelector("#language-select"),
};

const statusColours = {
  confirmed: "var(--confirmed)",
  "strong-evidence": "var(--strong)",
  hypothesis: "var(--hypothesis)",
  rejected: "#8f4d4d",
  unknown: "var(--unknown)",
};

function text(value, fallback = t("text.unknown")) {
  return typeof value === "string" && value.trim() ? value.trim() : fallback;
}

function initials(name) {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() || "")
    .join("");
}

function dateLabel(event) {
  if (!event?.date) return t("date.unknown");
  const date = event.date;
  if (date.kind === "exact") return date.value;
  if (date.kind === "month") return `${String(date.month).padStart(2, "0")}/${date.year}`;
  if (date.kind === "year") return String(date.year);
  return date.text || t("date.unknown");
}

function yearFromEvent(event) {
  if (!event?.date) return null;
  const date = event.date;
  if (date.kind === "exact") return String(date.value).slice(0, 4);
  if (date.kind === "month" || date.kind === "year") return String(date.year);
  const match = String(date.text || "").match(/\b(1[5-9]\d{2}|20\d{2})\b/);
  return match ? match[1] : null;
}

function lifespan(person) {
  const birth = person.events.find((event) => event.type === "birth");
  const death = person.events.find((event) => event.type === "death");
  const birthYear = yearFromEvent(birth);
  const deathYear = yearFromEvent(death);
  if (birthYear || deathYear) return `${birthYear || "?"}–${deathYear || ""}`;
  return person.privacy === "living" ? t("lifespan.living") : t("lifespan.unknown");
}

function primaryPlace(person) {
  const preferred = person.events.find((event) => event.type === "birth")
    || person.events.find((event) => event.type === "death")
    || person.events[0];
  return localePlace(preferred?.place?.name) || t("place.unknown");
}

// Rejected parentage edges are never drawn; every other status renders (with its
// own styling). There is no user toggle — the tree shows what has been modelled.
function relationshipVisible(relationship) {
  return relationship.status !== "rejected";
}

function createBadge(label, className = "") {
  const badge = document.createElement("span");
  badge.className = `badge ${className}`.trim();
  badge.textContent = label;
  return badge;
}

function createPersonCard(person, relationship, options = {}) {
  const button = document.createElement("button");
  const status = relationship?.status || "unknown";
  button.type = "button";
  button.className = `person-card ${options.root ? "root-card" : ""} ${options.reference ? "reference-card" : ""}`.trim();
  button.style.setProperty("--edge", statusColours[status] || statusColours.unknown);
  button.setAttribute("aria-label", t("card.aria", { name: person.name }));

  const avatar = document.createElement("span");
  avatar.className = "avatar";
  avatar.textContent = initials(person.name);

  const main = document.createElement("span");
  const name = document.createElement("strong");
  name.className = "person-name";
  name.textContent = person.name;
  const flag = nationalityFlag(person.nationality);
  if (flag) name.append(" ", flag);
  const years = document.createElement("span");
  years.className = "person-years";
  years.textContent = lifespan(person);
  const place = document.createElement("span");
  place.className = "person-place";
  place.textContent = primaryPlace(person);
  main.append(name, years, place);
  // Fall back to a text label only for a recorded nationality that has no flag.
  if (person.nationality && !flag) {
    const nationality = document.createElement("span");
    nationality.className = "person-nationality";
    nationality.textContent = person.nationality;
    main.append(nationality);
  }

  const meta = document.createElement("span");
  meta.className = "card-meta";
  if (relationship) {
    const label = person.hasConflict ? `${vocab("status", status)} ⚠` : vocab("status", status);
    meta.append(createBadge(label, status));
  } else if (person.hasConflict) {
    meta.append(createBadge(t("badge.conflict"), "conflict"));
  }
  if (person.sourceCount) meta.append(createBadge(tn("badge.source", person.sourceCount, { n: person.sourceCount })));
  if (person.privacy === "living") meta.append(createBadge(t("badge.private")));

  button.append(avatar, main, meta);
  button.title = t("card.title");
  button.addEventListener("click", () => {
    if (suppressClick) return;
    openDetails(person.id);
  });
  button.addEventListener("dblclick", (event) => {
    event.preventDefault();
    setRoot(person.id);
    closeDetails();
  });
  return button;
}

function createGenerationStop() {
  const stop = document.createElement("div");
  stop.className = "generation-stop";
  stop.textContent = t("tree.generationStop");
  return stop;
}

function createMarriageBadge(marriage) {
  const badge = document.createElement("div");
  badge.className = "marriage-badge";
  const year = yearFromEvent({ date: marriage.date });
  badge.textContent = year ? `⚭ ${year}` : "⚭";
  const detail = [localePlace(marriage.place), vocab("status", marriage.status)].filter(Boolean);
  badge.title = `${t("marriage.label")}${detail.length ? ` — ${detail.join(" · ")}` : ""}`;
  return badge;
}

function setRoot(personId) {
  if (!state.data.people[personId]) return;
  // Dismiss any open detail sheet — it was showing the previous person.
  if (elements.detailsPanel && !elements.detailsPanel.hidden) closeDetails();
  state.rootId = personId;
  state.focusId = personId;
  state.focusHistory = [];
  state.autoFit = true;
  if (elements.rootSelect) elements.rootSelect.value = personId;
  renderActive();
  scrollFocusIntoView();
  syncHash();
}

function createTreeNode(personId, relationship, depth, path, globalSeen) {
  const person = state.data.people[personId];
  if (!person) return null;

  state.visibleNodes += 1;
  const li = document.createElement("li");
  const status = relationship?.status || "unknown";
  li.style.setProperty("--edge", statusColours[status] || statusColours.unknown);

  const repeated = globalSeen.has(personId) && depth > 0;
  li.append(createPersonCard(person, relationship, { root: depth === 0, reference: repeated }));

  if (repeated || path.has(personId)) return li;

  const sexOrder = { male: 0, female: 1, unknown: 2 };
  const parents = (state.data.parentsByChild[personId] || [])
    .filter(relationshipVisible)
    .sort((a, b) => {
      const sa = sexOrder[state.data.people[a.parentId]?.sex] ?? 2;
      const sb = sexOrder[state.data.people[b.parentId]?.sex] ?? 2;
      return sa !== sb ? sa - sb : state.data.people[a.parentId]?.name.localeCompare(state.data.people[b.parentId]?.name || "") || 0;
    });

  if (!parents.length) return li;

  if (depth + 1 >= state.generations) {
    const ul = document.createElement("ul");
    const stopLi = document.createElement("li");
    stopLi.append(createGenerationStop());
    ul.append(stopLi);
    li.append(ul);
    return li;
  }

  globalSeen.add(personId);
  const nextPath = new Set(path);
  nextPath.add(personId);
  const ul = document.createElement("ul");

  const familyIds = new Set(parents.map((relationship) => relationship.familyId));
  if (parents.length === 2 && familyIds.size === 1) {
    const marriage = state.data.marriageByFamily?.[[...familyIds][0]];
    if (marriage) ul.append(createMarriageBadge(marriage));
  }

  for (const parentRelationship of parents) {
    const child = createTreeNode(
      parentRelationship.parentId,
      parentRelationship,
      depth + 1,
      nextPath,
      globalSeen,
    );
    if (child) ul.append(child);
  }

  if (ul.children.length) li.append(ul);
  return li;
}

function renderTree() {
  if (!state.data) return;
  state.visibleNodes = 0;
  elements.tree.replaceChildren();

  const root = state.data.people[state.rootId];
  if (!root) {
    elements.error.hidden = false;
    elements.error.textContent = t("tree.personUnavailable", { id: state.rootId });
    return;
  }

  const rootList = document.createElement("ul");
  const rootNode = createTreeNode(state.rootId, null, 0, new Set(), new Set());
  if (rootNode) rootList.append(rootNode);
  elements.tree.append(rootList);
  elements.visibleCount.textContent = String(state.visibleNodes);
  refreshZoom();
}

function naturalSize() {
  const stage = elements.treeStage;
  return { w: stage ? stage.offsetWidth : 0, h: stage ? stage.offsetHeight : 0 };
}

function applyZoom() {
  const { w, h } = naturalSize();
  elements.treeStage.style.transform = `scale(${state.zoom})`;
  elements.treeSizer.style.width = `${w * state.zoom}px`;
  elements.treeSizer.style.height = `${h * state.zoom}px`;
  elements.zoomLevel.textContent = `${Math.round(state.zoom * 100)}%`;
  elements.zoomIn.disabled = state.zoom >= MAX_ZOOM - 1e-3;
  elements.zoomOut.disabled = state.zoom <= MIN_ZOOM + 1e-3;
}

function centerScroll() {
  const viewport = elements.treeViewport;
  viewport.scrollLeft = Math.max(0, (viewport.scrollWidth - viewport.clientWidth) / 2);
  viewport.scrollTop = 0;
}

function fitZoom() {
  const viewport = elements.treeViewport;
  const { w } = naturalSize();
  const styles = getComputedStyle(viewport);
  const padX = parseFloat(styles.paddingLeft) + parseFloat(styles.paddingRight);
  const available = Math.max(1, viewport.clientWidth - padX);
  state.zoom = clamp(w ? available / w : 1, MIN_ZOOM, FIT_MAX_ZOOM);
  state.autoFit = true;
  applyZoom();
  centerScroll();
}

function setZoom(nextZoom, anchor) {
  const viewport = elements.treeViewport;
  const { w, h } = naturalSize();
  const previous = state.zoom;
  // Keep the anchor point (cursor, or the viewport centre by default) fixed on screen.
  const ax = anchor ? anchor.x : viewport.clientWidth / 2;
  const ay = anchor ? anchor.y : viewport.clientHeight / 2;
  const fracX = (viewport.scrollLeft + ax) / Math.max(1, w * previous);
  const fracY = (viewport.scrollTop + ay) / Math.max(1, h * previous);
  state.zoom = clamp(nextZoom, MIN_ZOOM, MAX_ZOOM);
  applyZoom();
  viewport.scrollLeft = fracX * w * state.zoom - ax;
  viewport.scrollTop = fracY * h * state.zoom - ay;
}

function refreshZoom() {
  if (!elements.treeStage) return;
  elements.treeControls.hidden = false;
  if (state.autoFit) fitZoom();
  else applyZoom();
}

function readHash() {
  const params = new URLSearchParams(location.hash.replace(/^#/, ""));
  return {
    root: params.get("root"),
    gen: params.get("gen"),
    sel: params.get("sel"),
    lang: params.get("lang"),
  };
}

function syncHash() {
  const params = new URLSearchParams();
  params.set("root", state.rootId);
  params.set("gen", String(state.generations));
  params.set("lang", state.locale);
  if (state.selected) params.set("sel", state.selected);
  const next = `#${params.toString()}`;
  if (next !== location.hash) history.replaceState(null, "", next);
}

function populatePersonSelect(query = "") {
  const normalised = query.trim().toLocaleLowerCase();
  const people = Object.values(state.data.people)
    .filter((person) => !normalised || person.name.toLocaleLowerCase().includes(normalised))
    .sort((a, b) => a.name.localeCompare(b.name));

  elements.rootSelect.replaceChildren();
  for (const person of people) {
    const option = document.createElement("option");
    option.value = person.id;
    option.textContent = `${person.name} (${person.id})`;
    option.selected = person.id === state.rootId;
    elements.rootSelect.append(option);
  }
}

function hideSearchResults() {
  if (!elements.searchResults) return;
  elements.searchResults.hidden = true;
  elements.searchResults.replaceChildren();
  elements.search.setAttribute("aria-expanded", "false");
}

// Navigate to a searched person: clear the box, dismiss the list, and re-root.
function selectSearchResult(personId) {
  elements.search.value = "";
  hideSearchResults();
  elements.search.blur();
  setRoot(personId);
}

// Live autocomplete: up to eight name matches, each a tappable row. Works by tap
// (mobile) and click/Enter (desktop); no submit gesture required.
function renderSearchResults(query) {
  const box = elements.searchResults;
  if (!box || !state.data) return;
  const normalised = query.trim().toLocaleLowerCase();
  box.replaceChildren();
  if (!normalised) {
    hideSearchResults();
    return;
  }
  const matches = Object.values(state.data.people)
    .filter((person) => person.name.toLocaleLowerCase().includes(normalised))
    .sort((a, b) => a.name.localeCompare(b.name))
    .slice(0, 8);
  if (!matches.length) {
    hideSearchResults();
    return;
  }
  for (const person of matches) {
    const item = document.createElement("button");
    item.type = "button";
    item.className = "search-result";
    item.setAttribute("role", "option");
    const name = document.createElement("span");
    name.className = "search-result-name";
    name.textContent = person.name;
    item.append(name);
    const years = person.privacy === "living" ? "" : lifespan(person);
    if (years) {
      const meta = document.createElement("span");
      meta.className = "search-result-meta";
      meta.textContent = years;
      item.append(meta);
    }
    item.addEventListener("click", () => selectSearchResult(person.id));
    box.append(item);
  }
  box.hidden = false;
  elements.search.setAttribute("aria-expanded", "true");
}

function applyStaticTranslations() {
  document.title = t("page.title");
  document.documentElement.lang = state.locale;
  for (const el of document.querySelectorAll("[data-i18n]")) {
    el.textContent = t(el.getAttribute("data-i18n"));
  }
  for (const el of document.querySelectorAll("[data-i18n-aria]")) {
    el.setAttribute("aria-label", t(el.getAttribute("data-i18n-aria")));
  }
  for (const el of document.querySelectorAll("[data-i18n-placeholder]")) {
    el.setAttribute("placeholder", t(el.getAttribute("data-i18n-placeholder")));
  }
}

function setLocale(locale) {
  const next = SUPPORTED_LOCALES.includes(locale) ? locale : "en";
  state.locale = next;
  i18n = createI18n(next);
  try { localStorage.setItem(LANG_STORAGE_KEY, next); } catch { /* storage unavailable */ }
  if (elements.languageSelect) elements.languageSelect.value = next;
  applyStaticTranslations();
  if (state.data) {
    renderActive();
    if (state.selected && !elements.detailsPanel.hidden) openDetails(state.selected);
  }
  syncHash();
}

function resolveInitialLocale(hashLang) {
  if (hashLang && SUPPORTED_LOCALES.includes(hashLang)) return hashLang;
  let stored = null;
  try { stored = localStorage.getItem(LANG_STORAGE_KEY); } catch { /* storage unavailable */ }
  if (stored && SUPPORTED_LOCALES.includes(stored)) return stored;
  const nav = typeof navigator !== "undefined"
    ? (navigator.languages && navigator.languages.length ? navigator.languages : [navigator.language])
    : [];
  return resolveLocale(nav);
}

// Localised date fragment for the biography (with a leading space), honouring
// uncertainty: approximate → "in about 1847", month/year → coarser phrasing.
function bioWhen(date) {
  if (!date || typeof date !== "object") return "";
  const months = t("bio.months").split("|");
  const yearIn = (v) => (String(v ?? "").match(/\b(\d{4})\b/) || [])[1];
  if (date.kind === "exact" && typeof date.value === "string") {
    const [y, m, d] = date.value.split("-").map(Number);
    return " " + t("bio.dateExact", { d, m: months[m - 1] || m, y });
  }
  if (date.kind === "month") return " " + t("bio.dateMonth", { m: months[date.month - 1] || date.month, y: date.year });
  if (date.kind === "year") return " " + t("bio.dateYear", { y: date.year });
  if (date.kind === "approximate") {
    const y = yearIn(date.text) || date.earliest;
    return y ? " " + t("bio.dateAbout", { y }) : "";
  }
  if (date.kind === "before") {
    const y = yearIn(date.text) || date.latest;
    return y ? " " + t("bio.dateBefore", { y }) : "";
  }
  if (date.kind === "after") {
    const y = yearIn(date.text) || date.earliest;
    return y ? " " + t("bio.dateAfter", { y }) : "";
  }
  return ""; // inferred / range / conflicting / unknown → left out of prose
}

function bioWhere(place) {
  return place ? " " + t("bio.inPlace", { place: localePlace(place) }) : "";
}

function joinAnd(items) {
  if (items.length <= 1) return items.join("");
  return `${items.slice(0, -1).join(", ")} ${t("list.and")} ${items[items.length - 1]}`;
}

// Compose the narrative biography paragraph from the projected, structured bio.
function biographyParagraph(person) {
  const bio = person.biography;
  if (!bio) return null;
  const sex = bio.sex || "unknown";
  const pronoun = sex === "male" ? t("bio.pronMale") : sex === "female" ? t("bio.pronFemale") : person.name;
  let leadUsed = false;
  const subject = () => {
    if (!leadUsed) { leadUsed = true; return person.name; }
    return pronoun;
  };
  const sentences = [];

  if (bio.sparse) {
    sentences.push(t("bio.sparse", { name: person.name }));
  } else {
    if (bio.birth) {
      const key = sex === "male" ? "bio.sonOf" : sex === "female" ? "bio.daughterOf" : "bio.childOf";
      const parents = bio.birth.parents.length ? t(key, { parents: joinAnd(bio.birth.parents) }) : "";
      sentences.push(t("bio.born", {
        subject: subject(),
        when: bioWhen(bio.birth.date),
        where: bioWhere(bio.birth.place),
        parents,
      }));
      if (bio.birth.emigratedToBrazil) sentences.push(t("bio.emigrated", { subject: subject() }));
    } else if (bio.parentsOnly && bio.children.length) {
      const key = sex === "male" ? "bio.parentOfFather" : sex === "female" ? "bio.parentOfMother" : "bio.parentOfParent";
      sentences.push(t(key, { subject: subject(), names: joinAnd(bio.children) }));
    }
    for (const marriage of bio.marriages) {
      sentences.push(t("bio.married", {
        subject: subject(),
        spouse: marriage.spouse,
        when: bioWhen(marriage.date),
        where: bioWhere(marriage.place),
      }));
    }
    if (!bio.parentsOnly && bio.children.length) {
      sentences.push(t("bio.children", { names: joinAnd(bio.children) }));
    }
    if (bio.occupations.length) {
      sentences.push(t("bio.worked", { subject: subject(), occupations: joinAnd(bio.occupations) }));
    }
    if (bio.death) {
      const age = bio.death.age
        ? t(bio.death.age.approx ? "bio.ageApprox" : "bio.age", { n: bio.death.age.years })
        : "";
      sentences.push(t("bio.died", {
        subject: subject(),
        when: bioWhen(bio.death.date),
        where: bioWhere(bio.death.place),
        age,
      }));
    }
  }

  if (!sentences.length) return null;
  const p = document.createElement("p");
  p.className = "biography";
  p.textContent = sentences.join(" ");
  return p;
}

// A concise kinship term for the subject → person path (ancestor paths only get
// a named term; anything else is just "relative").
function relationshipTerm(person) {
  const rel = person.lineage?.relationship;
  if (!rel) return null;
  if (rel.kind !== "ancestor") return t("rel.related");
  const pick = (m, f, n) => t(person.sex === "male" ? m : person.sex === "female" ? f : n);
  let term;
  if (rel.degree === 1) term = pick("rel.father", "rel.mother", "rel.parentNeutral");
  else if (rel.degree === 2) term = pick("rel.grandfather", "rel.grandmother", "rel.grandparentNeutral");
  else if (rel.degree === 3) term = pick("rel.greatGrandfather", "rel.greatGrandmother", "rel.greatGrandparentNeutral");
  else term = `${t("rel.ancestorDeep")} ${t("rel.generations", { n: rel.degree })}`;
  if (rel.side && rel.degree >= 2) {
    term += ` · ${t(rel.side === "paternal" ? "rel.paternalLine" : "rel.maternalLine")}`;
  }
  return term;
}

// The "Relationship to <subject>" block: a term line plus a clickable breadcrumb
// of the direct line from the subject to this person.
function relationshipContent(person) {
  const lineage = person.lineage;
  if (!lineage) return null;
  const wrap = document.createElement("div");
  wrap.className = "relationship";
  const term = relationshipTerm(person);
  if (term) {
    const label = document.createElement("p");
    label.className = "relationship-term";
    label.textContent = term;
    wrap.append(label);
  }
  const chain = document.createElement("p");
  chain.className = "relationship-chain";
  lineage.ids.forEach((id, index) => {
    if (index > 0) {
      const arrow = document.createElement("span");
      arrow.className = "relationship-arrow";
      arrow.textContent = "→";
      chain.append(arrow);
    }
    const name = state.data.people[id]?.name || id;
    if (index === lineage.ids.length - 1) {
      const current = document.createElement("strong");
      current.textContent = name;
      chain.append(current);
    } else {
      const link = document.createElement("button");
      link.type = "button";
      link.className = "relationship-link";
      link.textContent = name;
      link.addEventListener("click", () => openDetails(id));
      chain.append(link);
    }
  });
  wrap.append(chain);
  return wrap;
}

function section(title, content) {
  const wrapper = document.createElement("section");
  wrapper.className = "detail-section";
  const heading = document.createElement("h3");
  heading.textContent = title;
  wrapper.append(heading, content);
  return wrapper;
}

function list(items, emptyText) {
  if (!items.length) {
    const empty = document.createElement("p");
    empty.className = "empty-note";
    empty.textContent = emptyText;
    return empty;
  }
  const ul = document.createElement("ul");
  ul.className = "detail-list";
  for (const item of items) {
    const li = document.createElement("li");
    const segments = item.split("\n");
    for (let i = 0; i < segments.length; i++) {
      if (i > 0) li.append(document.createElement("br"));
      li.append(document.createTextNode(segments[i]));
    }
    ul.append(li);
  }
  return ul;
}

function fileLinkLabel(href) {
  const ext = href.split("?")[0].split(".").pop().toLowerCase();
  if (ext === "pdf") return t("file.viewDocument");
  if (["jpg", "jpeg", "png", "tif", "tiff", "gif", "webp"].includes(ext)) return t("file.viewImage");
  return t("file.viewFile");
}

function externalLink(href, label, extraClass = "") {
  const anchor = document.createElement("a");
  anchor.className = `source-link ${extraClass}`.trim();
  anchor.href = href;
  anchor.target = "_blank";
  anchor.rel = "noopener noreferrer";
  anchor.textContent = label;
  return anchor;
}

let readerKeyHandler = null;
function closeReader() {
  const overlay = document.querySelector(".reader-overlay");
  if (overlay) overlay.remove();
  if (readerKeyHandler) {
    document.removeEventListener("keydown", readerKeyHandler);
    readerKeyHandler = null;
  }
}

// The "Portrait / Retrato" layer: a right-side slide-over drawer opened from the
// "More details" link under the biography, holding the full evidence-tiered profile.
let portraitKeyHandler = null;
function closePortrait() {
  const overlay = document.querySelector(".portrait-overlay");
  if (overlay) overlay.remove();
  if (portraitKeyHandler) {
    document.removeEventListener("keydown", portraitKeyHandler);
    portraitKeyHandler = null;
  }
}
function openPortrait(person) {
  closePortrait();
  const text = localeText(person.profile, person.profilePt);
  if (!text) return;
  const overlay = document.createElement("div");
  overlay.className = "portrait-overlay";
  overlay.addEventListener("mousedown", (event) => {
    if (event.target === overlay) closePortrait();
  });

  const drawer = document.createElement("div");
  drawer.className = "portrait-drawer";

  const header = document.createElement("div");
  header.className = "portrait-drawer-header";
  const heading = document.createElement("div");
  heading.className = "portrait-drawer-heading";
  heading.textContent = `${t("detail.portrait")} — ${person.name}`;
  const closeBtn = document.createElement("button");
  closeBtn.type = "button";
  closeBtn.className = "reader-close";
  closeBtn.textContent = "✕";
  closeBtn.setAttribute("aria-label", t("reader.close"));
  closeBtn.addEventListener("click", closePortrait);
  header.append(heading, closeBtn);

  const body = document.createElement("div");
  body.className = "portrait portrait-drawer-body";
  renderPortrait(body, text);

  drawer.append(header, body);
  overlay.append(drawer);
  document.body.appendChild(overlay);

  portraitKeyHandler = (event) => {
    if (event.key === "Escape") closePortrait();
  };
  document.addEventListener("keydown", portraitKeyHandler);
}

// Render a transcript, styling only genuine gap/uncertainty markers ([torn],
// [illegible], [uncertain: …], [sic], [?], [...]) distinctly — editorial context
// brackets and page citations stay as normal text. Built with text nodes (no HTML).
function renderTranscript(container, text) {
  container.textContent = "";
  const gap = /\[(?:torn|stain|illegible|ileg[íi]ve\w*|uncertain\b[^\]]*|sic|\?|\.\.\.)\]/gi;
  let last = 0;
  let match;
  while ((match = gap.exec(text)) !== null) {
    if (match.index > last) {
      container.appendChild(document.createTextNode(text.slice(last, match.index)));
    }
    const span = document.createElement("span");
    span.className = "txn-gap";
    span.textContent = match[0];
    container.appendChild(span);
    last = match.index + match[0].length;
  }
  if (last < text.length) container.appendChild(document.createTextNode(text.slice(last)));
}

// Render an evidence-tiered "Portrait" narrative as light markdown: `## `/`### `
// headings, `- ` bullet lists, blank-line paragraphs, `**bold**`, `---` rules, and
// [PROVEN]/[INFERRED]/[LEAD]/[CONTEXTUAL]/[DOCUMENTED]/[OPEN]/[STRONG] evidence tags
// styled as chips. Built from DOM nodes (no innerHTML).
function renderPortrait(container, text) {
  container.textContent = "";
  const inline = (parent, s) => {
    const re = /\*\*(.+?)\*\*|\[(PROVEN|INFERRED|LEAD|CONTEXTUAL|DOCUMENTED|OPEN|STRONG)\]/g;
    let last = 0;
    let m;
    while ((m = re.exec(s)) !== null) {
      if (m.index > last) parent.appendChild(document.createTextNode(s.slice(last, m.index)));
      if (m[1] !== undefined) {
        const b = document.createElement("strong");
        b.textContent = m[1];
        parent.appendChild(b);
      } else {
        const span = document.createElement("span");
        span.className = "tier tier-" + m[2].toLowerCase();
        span.textContent = m[0];
        parent.appendChild(span);
      }
      last = m.index + m[0].length;
    }
    if (last < s.length) parent.appendChild(document.createTextNode(s.slice(last)));
  };
  let para = null;
  let ul = null;
  for (const raw of text.split("\n")) {
    const line = raw.replace(/\s+$/, "");
    if (!line.trim()) { para = null; ul = null; continue; }
    const mh = line.match(/^(#{2,4})\s+(.*)$/);
    if (mh) {
      para = null; ul = null;
      const h = document.createElement(mh[1].length <= 2 ? "h4" : "h5");
      h.className = "portrait-h";
      inline(h, mh[2]);
      container.appendChild(h);
      continue;
    }
    if (/^-{3,}$/.test(line.trim())) { para = null; ul = null; container.appendChild(document.createElement("hr")); continue; }
    if (/^\s*[-*]\s+/.test(line)) {
      para = null;
      if (!ul) { ul = document.createElement("ul"); ul.className = "portrait-list"; container.appendChild(ul); }
      const li = document.createElement("li");
      inline(li, line.replace(/^\s*[-*]\s+/, ""));
      ul.appendChild(li);
      continue;
    }
    ul = null;
    if (!para) { para = document.createElement("p"); para.className = "portrait-p"; container.appendChild(para); }
    else para.appendChild(document.createElement("br"));
    inline(para, line.trim());
  }
}

// A dependency-free pan/zoom pane: wheel OR two-finger pinch to zoom, one-finger
// drag to pan, double-tap/click resets. Pointer events cover mouse and touch.
function imagePane(src) {
  const pane = document.createElement("div");
  pane.className = "reader-image-pane";
  const img = document.createElement("img");
  img.className = "reader-img";
  img.src = src;
  img.alt = "";
  img.draggable = false;
  pane.appendChild(img);

  let scale = 1;
  let tx = 0;
  let ty = 0;
  const clampScale = (value) => Math.min(12, Math.max(0.4, value));
  const apply = () => {
    img.style.transform = `translate(${tx}px, ${ty}px) scale(${scale})`;
  };

  pane.addEventListener("wheel", (event) => {
    event.preventDefault();
    scale = clampScale(scale * (event.deltaY < 0 ? 1.15 : 1 / 1.15));
    apply();
  }, { passive: false });

  // Track active pointers so one finger pans and two fingers pinch-zoom.
  const pointers = new Map();
  let panStartX = 0;
  let panStartY = 0;
  let pinchDist = 0;
  let pinchScale = 1;
  const twoPointerDistance = () => {
    const [a, b] = [...pointers.values()];
    return Math.hypot(a.x - b.x, a.y - b.y);
  };
  const resumePan = () => {
    const [p] = [...pointers.values()];
    if (p) {
      panStartX = p.x - tx;
      panStartY = p.y - ty;
    }
  };

  pane.addEventListener("pointerdown", (event) => {
    pane.setPointerCapture(event.pointerId);
    pointers.set(event.pointerId, { x: event.clientX, y: event.clientY });
    if (pointers.size === 1) {
      panStartX = event.clientX - tx;
      panStartY = event.clientY - ty;
      pane.classList.add("grabbing");
    } else if (pointers.size === 2) {
      pinchDist = twoPointerDistance();
      pinchScale = scale;
    }
  });
  pane.addEventListener("pointermove", (event) => {
    if (!pointers.has(event.pointerId)) return;
    pointers.set(event.pointerId, { x: event.clientX, y: event.clientY });
    if (pointers.size >= 2) {
      if (pinchDist > 0) {
        scale = clampScale(pinchScale * (twoPointerDistance() / pinchDist));
        apply();
      }
    } else if (pointers.size === 1) {
      tx = event.clientX - panStartX;
      ty = event.clientY - panStartY;
      apply();
    }
  });
  const endPointer = (event) => {
    if (pane.hasPointerCapture?.(event.pointerId)) pane.releasePointerCapture(event.pointerId);
    pointers.delete(event.pointerId);
    if (pointers.size < 2) pinchDist = 0;
    if (pointers.size === 1) resumePan();
    if (pointers.size === 0) pane.classList.remove("grabbing");
  };
  pane.addEventListener("pointerup", endPointer);
  pane.addEventListener("pointercancel", endPointer);

  pane.addEventListener("dblclick", () => {
    scale = 1;
    tx = 0;
    ty = 0;
    apply();
  });
  return pane;
}

// The split "facsimile + transcript" reading view.
function openReader(source) {
  closeReader();
  const overlay = document.createElement("div");
  overlay.className = "reader-overlay";
  overlay.addEventListener("mousedown", (event) => {
    if (event.target === overlay) closeReader();
  });

  const dialog = document.createElement("div");
  dialog.className = "reader-dialog";

  const header = document.createElement("div");
  header.className = "reader-header";
  const heading = document.createElement("div");
  heading.className = "reader-heading";
  const hid = document.createElement("span");
  hid.className = "source-id";
  hid.textContent = source.id;
  heading.append(hid, document.createTextNode(source.title || source.id));
  const closeBtn = document.createElement("button");
  closeBtn.type = "button";
  closeBtn.className = "reader-close";
  closeBtn.textContent = "✕";
  closeBtn.setAttribute("aria-label", t("reader.close"));
  closeBtn.addEventListener("click", closeReader);
  header.append(heading, closeBtn);

  const body = document.createElement("div");
  body.className = "reader-body";
  let leftPane;
  if (source.fileType === "pdf") {
    leftPane = document.createElement("iframe");
    leftPane.className = "reader-pdf";
    leftPane.src = source.file;
    leftPane.title = source.title || source.id;
  } else {
    leftPane = imagePane(source.file);
  }

  const right = document.createElement("div");
  right.className = "reader-transcript-pane";
  const toggle = document.createElement("div");
  toggle.className = "reader-toggle";
  const txnBtn = document.createElement("button");
  txnBtn.type = "button";
  txnBtn.className = "reader-tab";
  txnBtn.textContent = t("reader.transcription");
  const absBtn = document.createElement("button");
  absBtn.type = "button";
  absBtn.className = "reader-tab";
  absBtn.textContent = t("reader.abstract");
  const textEl = document.createElement("div");
  textEl.className = "reader-transcript";
  const showTxn = () => {
    txnBtn.classList.add("active");
    absBtn.classList.remove("active");
    if (source.transcription)
      renderTranscript(textEl, localeText(source.transcription, source.transcriptionPt));
    else textEl.textContent = t("reader.noTranscript");
  };
  const showAbs = () => {
    absBtn.classList.add("active");
    txnBtn.classList.remove("active");
    textEl.textContent = localeText(source.abstract, source.abstractPt) || t("reader.noTranscript");
  };
  txnBtn.addEventListener("click", showTxn);
  absBtn.addEventListener("click", showAbs);
  if (source.transcription && source.abstract) toggle.append(txnBtn, absBtn);
  right.append(toggle, textEl);
  if (source.transcription) showTxn();
  else if (source.abstract) showAbs();
  else textEl.textContent = t("reader.noTranscript");

  body.append(leftPane, right);
  dialog.append(header, body);
  if (source.fileType !== "pdf") {
    const hint = document.createElement("div");
    hint.className = "reader-hint";
    hint.textContent = t("reader.zoomHint");
    dialog.append(hint);
  }
  overlay.appendChild(dialog);
  document.body.appendChild(overlay);
  readerKeyHandler = (event) => {
    if (event.key === "Escape") closeReader();
  };
  document.addEventListener("keydown", readerKeyHandler);
}

function readerOpenButton(source) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = "source-link reader-open";
  button.textContent = t("reader.open");
  button.addEventListener("click", () => openReader(source));
  return button;
}

// Classify a source into one of four display buckets so the detail panel always
// shows records in life-event order: birth/baptism → marriage → death/burial →
// everything else. Matches on both recordType and title (case-insensitive).
function sourceBucket(source) {
  const hay = `${source.recordType || ""} ${source.title || ""}`.toLowerCase();
  if (/bapti[sz]|birth|nascimento|batismo|batizado/.test(hay)) return 1;
  if (/marriage|casamento|matrim[oô]ni|wed/.test(hay)) return 2;
  if (/death|óbito|obito|burial|faleci/.test(hay)) return 3;
  return 4;
}

function sourceList(sources) {
  if (!sources.length) {
    const empty = document.createElement("p");
    empty.className = "empty-note";
    empty.textContent = t("empty.sources");
    return empty;
  }

  // Stable sort into four display buckets; existing order is preserved within
  // each bucket (Array.prototype.sort is stable in all modern environments).
  const sorted = sources.slice().sort((a, b) => sourceBucket(a) - sourceBucket(b));

  const ul = document.createElement("ul");
  ul.className = "source-list";

  for (const source of sorted) {
    const li = document.createElement("li");
    li.className = source.uncertain ? "source-item source-flagged" : "source-item";

    const title = document.createElement("div");
    title.className = "source-title";
    const id = document.createElement("span");
    id.className = "source-id";
    id.textContent = source.id;
    title.append(id, document.createTextNode(source.title || source.id));

    const metaBits = [source.recordType, source.sourceForm, source.quality].filter(Boolean);
    const meta = document.createElement("div");
    meta.className = "source-meta";
    meta.textContent = metaBits.join(" · ");

    const actions = document.createElement("div");
    actions.className = "source-actions";
    if (source.file && source.fileType !== "other") actions.append(readerOpenButton(source));
    if (source.file) actions.append(externalLink(source.file, fileLinkLabel(source.file)));
    if (source.url) actions.append(externalLink(source.url, t("source.recordLink"), "external"));
    if (!source.file && !source.url) {
      const none = document.createElement("span");
      none.className = "source-none";
      none.textContent = t("source.noFile");
      actions.append(none);
    }
    if (source.uncertain) actions.append(createBadge(t("source.uncertain"), "conflict"));
    if (source.involvesLiving) actions.append(createBadge(t("badge.private")));

    const nodes = [title];
    if (metaBits.length) nodes.push(meta);
    nodes.push(actions);
    if (source.transcription) {
      const transcription = document.createElement("p");
      transcription.className = "source-transcription";
      transcription.textContent = localeText(source.transcription, source.transcriptionPt);
      nodes.push(transcription);
    }
    if (source.abstract) {
      const abstract = document.createElement("p");
      abstract.className = "source-abstract";
      abstract.textContent = localeText(source.abstract, source.abstractPt);
      nodes.push(abstract);
    }
    if (source.limitation) {
      const limitation = document.createElement("p");
      limitation.className = "source-limitation";
      limitation.textContent = `⚠ ${source.limitation}`;
      nodes.push(limitation);
    }

    li.append(...nodes);
    ul.append(li);
  }

  return ul;
}

function fanList(refs) {
  if (!refs.length) {
    const empty = document.createElement("p");
    empty.className = "empty-note";
    empty.textContent = t("empty.fan");
    return empty;
  }

  const ul = document.createElement("ul");
  ul.className = "source-list";

  for (const ref of refs) {
    const li = document.createElement("li");
    li.className = "source-item";

    const title = document.createElement("div");
    title.className = "source-title";
    const id = document.createElement("span");
    id.className = "source-id";
    id.textContent = ref.id;
    title.append(id, document.createTextNode(ref.title || ref.id));

    const metaBits = [ref.role, ref.recordCategory, localePlace(ref.place)].filter(Boolean);
    const meta = document.createElement("div");
    meta.className = "source-meta";
    meta.textContent = metaBits.join(" · ");

    const actions = document.createElement("div");
    actions.className = "source-actions";
    if (ref.file && ref.fileType !== "other") actions.append(readerOpenButton(ref));
    if (ref.file) actions.append(externalLink(ref.file, fileLinkLabel(ref.file)));
    if (ref.url) actions.append(externalLink(ref.url, t("source.recordLink"), "external"));

    const nodes = [title];
    if (metaBits.length) nodes.push(meta);
    if (actions.childElementCount) nodes.push(actions);
    if (ref.transcription) {
      const transcription = document.createElement("p");
      transcription.className = "source-transcription";
      transcription.textContent = localeText(ref.transcription, ref.transcriptionPt);
      nodes.push(transcription);
    }

    li.append(...nodes);
    ul.append(li);
  }

  return ul;
}

function openDetails(personId) {
  const person = state.data.people[personId];
  if (!person) return;
  closePortrait();

  elements.detailsId.textContent = person.id;
  elements.detailsTitle.textContent = person.name;
  elements.detailsLifespan.textContent = lifespan(person);
  elements.detailsContent.replaceChildren();

  if (person.hasConflict) {
    const caution = document.createElement("p");
    caution.className = "detail-caution";
    caution.textContent = t("detail.caution");
    elements.detailsContent.append(caution);
  }

  const bio = biographyParagraph(person);
  if (bio) elements.detailsContent.append(section(t("detail.biography"), bio));

  if (localeText(person.profile, person.profilePt)) {
    const moreWrap = document.createElement("div");
    moreWrap.className = "portrait-more";
    const moreBtn = document.createElement("button");
    moreBtn.type = "button";
    moreBtn.className = "portrait-more-btn";
    moreBtn.textContent = t("detail.moreDetails");
    moreBtn.addEventListener("click", () => openPortrait(person));
    moreWrap.appendChild(moreBtn);
    elements.detailsContent.append(moreWrap);
  }

  const relationship = relationshipContent(person);
  if (relationship) {
    const subjectName = (state.data.people["P-0001"]?.name || "").split(" ")[0] || "";
    elements.detailsContent.append(section(t("detail.relationship", { name: subjectName }), relationship));
  }

  const facts = document.createElement("dl");
  facts.className = "detail-grid";
  const factRows = [
    [t("fact.privacy"), vocab("privacy", person.privacy)],
    [t("fact.sources"), String(person.sourceCount)],
    [t("fact.contextRefs"), String((person.fanReferences || []).length)],
    [t("fact.birthplace"), localePlace(person.events.find((event) => event.type === "birth")?.place?.name) || t("value.notEstablished")],
    [t("fact.nationality"), nationalityValue(person.nationality)],
    [t("fact.deathplace"), localePlace(person.events.find((event) => event.type === "death")?.place?.name) || t("value.notEstablished")],
  ];
  for (const [term, value] of factRows) {
    const dt = document.createElement("dt");
    dt.textContent = term;
    const dd = document.createElement("dd");
    if (value instanceof Node) dd.append(value);
    else dd.textContent = text(value);
    facts.append(dt, dd);
  }
  elements.detailsContent.append(section(t("detail.overview"), facts));

  const eventItems = person.events.map((event) => {
    const place = event.place?.name ? ` · ${localePlace(event.place.name)}` : "";
    return `${vocab("event", event.type)} · ${dateLabel(event)}${place} · ${vocab("status", event.status)}`;
  });
  elements.detailsContent.append(section(t("detail.events"), list(eventItems, t("empty.events"))));

  const parentItems = (state.data.parentsByChild[personId] || [])
    .filter(relationshipVisible)
    .map((relationship) => {
      const parent = state.data.people[relationship.parentId];
      return `${parent?.name || relationship.parentId} — ${vocab("status", relationship.status)}`;
    });
  elements.detailsContent.append(section(t("detail.parents"), list(parentItems, t("empty.parents"))));

  const siblingItems = (person.siblings || []).map((sib) =>
    sib.lifespan ? `${sib.name} (${sib.lifespan})` : sib.name,
  );
  elements.detailsContent.append(section(t("detail.siblings"), list(siblingItems, t("empty.siblings"))));

  if (person.privacy !== "living") {
    const marriageItems = person.spouses.map((spouse) => {
      const bits = [];
      const year = spouse.marriage ? yearFromEvent({ date: spouse.marriage.date }) : null;
      if (year) bits.push(t("marriage.year", { year }));
      if (spouse.marriage?.place) bits.push(localePlace(spouse.marriage.place));
      if (spouse.marriage?.status) bits.push(vocab("status", spouse.marriage.status));
      return bits.length ? `${spouse.name} — ${bits.join(" · ")}` : spouse.name;
    });
    elements.detailsContent.append(section(t("detail.marriages"), list(marriageItems, t("empty.partners"))));

    const childItems = (person.children || []).map((child) =>
      child.lifespan ? `${child.name} (${child.lifespan})` : child.name,
    );
    elements.detailsContent.append(section(t("detail.children"), list(childItems, t("empty.children"))));

    const occupationItems = person.occupations.map((occupation) => {
      const src = occupation.sourceIds.length ? ` · ${occupation.sourceIds.join(", ")}` : "";
      return occupation.note ? `${occupation.value}${src} — ${occupation.note}` : `${occupation.value}${src}`;
    });
    elements.detailsContent.append(section(t("detail.occupation"), list(occupationItems, t("empty.occupation"))));

    elements.detailsContent.append(section(t("detail.recordedNames"), list(person.nameVariants, t("empty.names"))));
    elements.detailsContent.append(section(t("detail.sources"), sourceList(person.sources)));
    elements.detailsContent.append(
      section(t("detail.fan"), fanList(person.fanReferences || [])),
    );
    elements.detailsContent.append(
      section(t("detail.notes"), list((person.notes || []).map((note) => localeText(note)), t("empty.notes"))),
    );
  } else {
    const privacy = document.createElement("p");
    privacy.className = "empty-note";
    privacy.textContent = t("detail.livingMinimised");
    elements.detailsContent.append(section(t("detail.privacy"), privacy));
  }

  if (!elements.detailsPanel.contains(document.activeElement)) {
    lastFocused = document.activeElement;
  }
  elements.detailsPanel.hidden = false;
  elements.backdrop.hidden = false;
  elements.closeDetails.focus();
  state.selected = personId;
  syncHash();
}

function closeDetails() {
  closePortrait();
  elements.detailsPanel.hidden = true;
  elements.backdrop.hidden = true;
  state.selected = null;
  syncHash();
  if (lastFocused && lastFocused.isConnected && typeof lastFocused.focus === "function") {
    lastFocused.focus();
  }
  lastFocused = null;
}

// ---------- Mobile focus view ----------
// A phone-native alternative to the horizontal pedigree: one person centred at a
// time, with tappable rows for parents, partners, children and siblings. It reuses
// the same projected data and presentation helpers as the desktop tree; only the
// layout differs, chosen at runtime by viewport width.

const MOBILE_QUERY = window.matchMedia("(max-width: 700px)");
const isMobile = () => MOBILE_QUERY.matches;

// One tappable relation row. Rows for a modelled person we can re-centre on are
// buttons; documented-only relations (no entity) are inert.
function mobileRelationRow(id, name, meta) {
  const target = id && state.data.people[id];
  const row = document.createElement(target ? "button" : "div");
  row.className = `mobile-row${target ? "" : " is-static"}`;
  if (target) {
    row.type = "button";
    row.addEventListener("click", () => focusPerson(id));
  }
  const label = document.createElement("span");
  label.className = "mobile-row-name";
  label.textContent = name;
  const flag = target ? nationalityFlag(target.nationality) : null;
  if (flag) label.append(" ", flag);
  row.append(label);
  const detail = target ? lifespan(target) : meta;
  if (detail) {
    const m = document.createElement("span");
    m.className = "mobile-row-meta";
    m.textContent = detail;
    row.append(m);
  }
  if (target) {
    const chevron = document.createElement("span");
    chevron.className = "mobile-row-chevron";
    chevron.setAttribute("aria-hidden", "true");
    chevron.textContent = "›";
    row.append(chevron);
  }
  return row;
}

function mobileSection(title, rows, emptyText) {
  const section = document.createElement("section");
  section.className = "mobile-section";
  const heading = document.createElement("h3");
  heading.className = "mobile-section-title";
  heading.textContent = title;
  section.append(heading);
  if (!rows.length) {
    const empty = document.createElement("p");
    empty.className = "mobile-empty";
    empty.textContent = emptyText;
    section.append(empty);
  } else {
    const list = document.createElement("div");
    list.className = "mobile-list";
    for (const row of rows) list.append(row);
    section.append(list);
  }
  return section;
}

function focusPerson(personId) {
  if (!state.data?.people[personId] || personId === state.focusId) return;
  // Dismiss any open detail sheet — it was showing the previous person.
  if (elements.detailsPanel && !elements.detailsPanel.hidden) closeDetails();
  state.focusHistory.push(state.focusId);
  state.focusId = personId;
  renderMobileFocus();
  scrollFocusIntoView();
}

function focusBack() {
  if (!state.focusHistory.length) return;
  state.focusId = state.focusHistory.pop();
  renderMobileFocus();
  scrollFocusIntoView();
}

function renderMobileFocus() {
  const container = elements.mobileView;
  if (!container || !state.data) return;
  const person = state.data.people[state.focusId] || state.data.people[state.rootId];
  container.replaceChildren();
  if (!person) return;

  const nav = document.createElement("div");
  nav.className = "mobile-nav";
  if (state.focusHistory.length) {
    const back = document.createElement("button");
    back.type = "button";
    back.className = "mobile-nav-btn";
    back.textContent = `‹ ${t("mobile.back")}`;
    back.addEventListener("click", focusBack);
    nav.append(back);
  }
  const home = document.createElement("button");
  home.type = "button";
  home.className = "mobile-nav-btn mobile-nav-home";
  home.textContent = `⌂ ${t("mobile.home")}`;
  home.addEventListener("click", () => focusPerson("P-0001"));
  nav.append(home);
  container.append(nav);

  const head = document.createElement("div");
  head.className = "mobile-focus-head";
  const title = document.createElement("h2");
  title.className = "mobile-focus-name";
  title.textContent = person.name;
  const flag = nationalityFlag(person.nationality);
  if (flag) title.append(" ", flag);
  head.append(title);
  const years = lifespan(person);
  if (years) {
    const yearsLine = document.createElement("p");
    yearsLine.className = "mobile-focus-years";
    yearsLine.textContent = years;
    head.append(yearsLine);
  }
  const relTerm = relationshipTerm(person);
  if (relTerm && person.id !== "P-0001") {
    const chip = document.createElement("p");
    chip.className = "mobile-focus-rel";
    const subjectName = (state.data.people["P-0001"]?.name || "").split(" ")[0] || "";
    chip.textContent = `${t("detail.relationship", { name: subjectName })}: ${relTerm}`;
    head.append(chip);
  }
  const detailsButton = document.createElement("button");
  detailsButton.type = "button";
  detailsButton.className = "mobile-details-btn";
  detailsButton.textContent = `${t("mobile.fullDetails")} ›`;
  detailsButton.addEventListener("click", () => openDetails(person.id));
  head.append(detailsButton);
  container.append(head);

  const parentIds = [
    ...new Set(
      (state.data.parentsByChild[person.id] || [])
        .filter(relationshipVisible)
        .map((entry) => entry.parentId),
    ),
  ];
  const parentRows = parentIds.map((pid) => mobileRelationRow(pid, state.data.people[pid]?.name || pid));
  container.append(mobileSection(t("detail.parents"), parentRows, t("empty.parents")));

  const spouseRows = (person.spouses || []).map((spouse) =>
    mobileRelationRow(spouse.id, spouse.name, spouse.marriage ? bioWhen(spouse.marriage) : null),
  );
  container.append(mobileSection(t("detail.marriages"), spouseRows, t("empty.partners")));

  const childRows = (person.children || []).map((child) => mobileRelationRow(child.id, child.name));
  container.append(mobileSection(t("detail.children"), childRows, t("empty.children")));

  const siblingRows = (person.siblings || []).map((sibling) => mobileRelationRow(sibling.id, sibling.name));
  container.append(mobileSection(t("detail.siblings"), siblingRows, t("empty.siblings")));

  const hint = document.createElement("p");
  hint.className = "mobile-hint";
  hint.textContent = t("mobile.tapHint");
  container.append(hint);
}

// On a navigation (tapping a relation, searching, re-rooting), bring the focus
// view to the top of the screen so the person's card is visible without scrolling
// past the header/toolbar. Only meaningful on the mobile layout.
function scrollFocusIntoView() {
  if (isMobile() && elements.mobileView) {
    elements.mobileView.scrollIntoView({ block: "start", behavior: "auto" });
  }
}

// Render whichever layout the current viewport calls for. The desktop pedigree and
// the mobile focus view live in separate containers; only the active one is built.
function renderActive() {
  document.body.classList.toggle("is-mobile", isMobile());
  if (isMobile()) {
    if (elements.treeShell) elements.treeShell.hidden = true;
    elements.mobileView.hidden = false;
    renderMobileFocus();
  } else {
    elements.mobileView.hidden = true;
    if (elements.treeShell) elements.treeShell.hidden = false;
    renderTree();
  }
}

function bindEvents() {
  // Switch layouts when the viewport crosses the mobile breakpoint (e.g. rotate).
  MOBILE_QUERY.addEventListener("change", () => {
    if (state.data) renderActive();
  });

  elements.rootSelect.addEventListener("change", () => {
    setRoot(elements.rootSelect.value);
  });

  elements.generationLimit.addEventListener("change", () => {
    state.generations = Number(elements.generationLimit.value);
    state.autoFit = true;
    renderTree();
    syncHash();
  });

  elements.zoomIn.addEventListener("click", () => { state.autoFit = false; setZoom(state.zoom * 1.2); });
  elements.zoomOut.addEventListener("click", () => { state.autoFit = false; setZoom(state.zoom / 1.2); });
  elements.zoomFit.addEventListener("click", () => fitZoom());

  elements.treeViewport.addEventListener("wheel", (event) => {
    // Scroll/trackpad zooms the tree, anchored on the cursor (map-style). Shift+wheel
    // still scrolls the canvas, for anyone who prefers panning by wheel.
    if (event.shiftKey) return;
    event.preventDefault();
    state.autoFit = false;
    const rect = elements.treeViewport.getBoundingClientRect();
    const anchor = { x: event.clientX - rect.left, y: event.clientY - rect.top };
    const factor = event.deltaY < 0 ? 1.1 : 1 / 1.1;
    setZoom(state.zoom * factor, anchor);
  }, { passive: false });

  window.addEventListener("resize", () => { if (state.autoFit) fitZoom(); });

  // Drag anywhere on the canvas to pan; a real drag suppresses the card click.
  const viewport = elements.treeViewport;
  viewport.addEventListener("pointerdown", (event) => {
    if (event.button !== 0) return;
    panState = {
      id: event.pointerId,
      x: event.clientX,
      y: event.clientY,
      left: viewport.scrollLeft,
      top: viewport.scrollTop,
      moved: false,
    };
  });
  viewport.addEventListener("pointermove", (event) => {
    if (!panState || event.pointerId !== panState.id) return;
    const dx = event.clientX - panState.x;
    const dy = event.clientY - panState.y;
    if (!panState.moved && Math.hypot(dx, dy) < 5) return;
    if (!panState.moved) {
      panState.moved = true;
      viewport.classList.add("is-panning");
      viewport.setPointerCapture(panState.id);
    }
    viewport.scrollLeft = panState.left - dx;
    viewport.scrollTop = panState.top - dy;
  });
  const endPan = () => {
    if (!panState) return;
    if (panState.moved) {
      suppressClick = true;
      setTimeout(() => { suppressClick = false; }, 0);
    }
    try { viewport.releasePointerCapture(panState.id); } catch { /* already released */ }
    viewport.classList.remove("is-panning");
    panState = null;
  };
  viewport.addEventListener("pointerup", endPan);
  viewport.addEventListener("pointercancel", endPan);

  // Live search: typing shows a tappable results list; tapping a result navigates
  // to that person. This does not depend on a submit gesture (the mobile keyboard's
  // Go key / the native "search" event were unreliable), so a tap always selects.
  elements.search.addEventListener("input", () => renderSearchResults(elements.search.value));
  elements.search.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      const first = elements.searchResults?.querySelector(".search-result");
      if (first) first.click();
    } else if (event.key === "Escape") {
      hideSearchResults();
    }
  });
  // Hide the list on blur, but after a beat so a tap on a result registers first.
  elements.search.addEventListener("blur", () => {
    setTimeout(hideSearchResults, 200);
  });

  elements.reset.addEventListener("click", () => {
    state.rootId = state.data.people["P-0001"] ? "P-0001" : Object.keys(state.data.people)[0];
    state.focusId = state.rootId;
    state.focusHistory = [];
    state.generations = 4;
    state.autoFit = true;
    elements.generationLimit.value = "4";
    elements.search.value = "";
    populatePersonSelect();
    elements.rootSelect.value = state.rootId;
    renderActive();
    syncHash();
  });

  if (elements.languageSelect) {
    elements.languageSelect.addEventListener("change", () => setLocale(elements.languageSelect.value));
  }

  elements.closeDetails.addEventListener("click", closeDetails);
  elements.backdrop.addEventListener("click", closeDetails);
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !elements.detailsPanel.hidden) closeDetails();
  });
}

async function initialise() {
  bindEvents();
  // Resolve the display language before anything renders, so the chrome and the
  // loading text appear localised immediately.
  state.locale = resolveInitialLocale(readHash().lang);
  i18n = createI18n(state.locale);
  if (elements.languageSelect) elements.languageSelect.value = state.locale;
  applyStaticTranslations();
  try {
    const response = await fetch("/api/tree", { cache: "no-store" });
    if (!response.ok) throw new Error(t("error.httpStatus", { status: response.status }));
    state.data = await response.json();
    state.rootId = state.data.people["P-0001"] ? "P-0001" : Object.keys(state.data.people)[0];

    // Restore a shared/bookmarked view from the URL hash.
    const hash = readHash();
    if (hash.root && state.data.people[hash.root]) state.rootId = hash.root;
    if (hash.gen && /^([2-9]|1[0-9]|20)$/.test(hash.gen)) state.generations = Number(hash.gen);
    state.focusId = state.rootId;

    populatePersonSelect();
    elements.rootSelect.value = state.rootId;
    elements.generationLimit.value = String(state.generations);
    elements.personCount.textContent = String(Object.keys(state.data.people).length);
    elements.familyCount.textContent = String(state.data.familyCount);
    elements.sourceCount.textContent = String(Object.keys(state.data.sources).length);
    elements.loading.hidden = true;
    renderActive();
    if (hash.sel && state.data.people[hash.sel]) openDetails(hash.sel);
    else syncHash();
  } catch (error) {
    elements.loading.hidden = true;
    elements.error.hidden = false;
    elements.error.textContent = t("error.loadFailed", { message: error.message });
  }
}

initialise();
