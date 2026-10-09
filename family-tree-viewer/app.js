import { createI18n, resolveLocale, SUPPORTED_LOCALES } from "./i18n.js";
import { load as parseYaml } from "./vendor/js-yaml.mjs";
import {
  computeBranches,
  entryBranches,
  entryInScope,
  inScope,
  isCurated,
  normaliseScope,
  parseScope,
  reorderStory,
  scopeRoot,
  scopeSize,
  serialiseScope,
  surnameIndex,
  SUBJECT_ID,
  updateKey,
} from "./branches.js";

const LANG_STORAGE_KEY = "armond-viewer-lang";
// Set once the first-run guide has been shown, so it never auto-opens again (the
// "? Help" button always reopens it on demand). Bump the suffix to re-introduce it.
const GUIDE_STORAGE_KEY = "armond-viewer-guide-seen-v1";
// The family branches a viewer chose ("all" or e.g. "muniz,bohrer"); absent until the
// first-visit picker has been answered.
const BRANCH_STORAGE_KEY = "armond-viewer-branches";
// The curated What's new entries this device has already seen, for the unread badge.
const UPDATES_SEEN_KEY = "armond-updates-seen-v1";

// Live visitor greeting ("you're visiting from <flag> <country> · you are
// visitor #N"). Powered by a small Cloudflare Worker + KV the owner deploys (see
// workers/visitor-counter/): the country comes from Cloudflare's edge, the number
// from a KV counter. Leave empty to disable — the greeting simply stays hidden.
const VISITOR_API = "https://family-visitor-counter.juan-armond.workers.dev";
const VISITOR_NUM_KEY = "armond-viewer-visitor-number";

// AI family-history assistant. Powered by a Cloudflare Worker the owner deploys
// (see workers/family-assistant/): it answers questions grounded only in this
// archive's data via Gemini, and streams the reply back as plain text. Leave empty
// to disable — the "Ask" button simply stays hidden until the Worker URL is set.
// A localStorage key "armond-assistant-api" overrides it (for local testing against
// `wrangler dev`, or pointing the live site at a staging Worker) without a code change.
const CONFIGURED_ASSISTANT_API = "https://family-assistant.juan-armond.workers.dev";
let ASSISTANT_API = CONFIGURED_ASSISTANT_API;
try {
  const override = localStorage.getItem("armond-assistant-api");
  if (override) ASSISTANT_API = override;
} catch { /* storage unavailable — use the configured default */ }

// "What's new" push notifications. Powered by a Cloudflare Worker the owner deploys (see
// workers/family-notify/): devices register anonymously and the deploy workflow sends one
// summary notification per publish. The opt-in bar stays hidden until the Worker's /health
// answers with its public key, so the site is safe to deploy before the Worker exists.
const NOTIFY_API = "https://family-notify.juan-armond.workers.dev";

// Viewer key for personalisation — set from ?viewer= param or detected by the Worker when
// someone types "I am Felipe" / "Eu sou Hugo" in the chat. Persisted for the browser session.
const VIEWER_KEY_PARAM = (() => {
  try { return new URLSearchParams(location.search).get("viewer") || ""; } catch { return ""; }
})();
let sessionViewerKey = VIEWER_KEY_PARAM;
function getViewerKey() { return sessionViewerKey; }

const state = {
  data: null,
  rootId: "P-0001",
  generations: 4,
  // Persons whose ancestry visibility is flipped from the generation-limit default by a card's
  // +/- toggle: a shallow branch collapsed shut, or a deep branch opened past the base limit.
  toggled: new Set(),
  visibleNodes: 0,
  zoom: 1,
  autoFit: true,
  selected: null,
  locale: "en",
  // Mobile "focus view": the person currently centred (null shows the home screen), and the
  // back stack. homeView picks a home sub-screen: null, "surnames" or "surname:<key>".
  focusId: null,
  focusHistory: [],
  homeView: null,
  // Family branches ("the four rivers", see branches.js) and the viewer's choice of them; an
  // empty scope means everything. searchAll / updatesAll widen one list past the scope;
  // storyFullOrder reads the story in its written order.
  branches: null,
  scope: new Set(),
  searchAll: false,
  updatesAll: false,
  storyFullOrder: false,
  // Live visitor greeting payload once fetched: { number, country }.
  visitor: null,
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

const MIN_ZOOM = 0.25;
const MAX_ZOOM = 1;
const FIT_MAX_ZOOM = 1; // auto-fit never magnifies past 100%
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
  openStory: document.querySelector("#open-story"),
  storyPanel: document.querySelector("#story-panel"),
  storyBackdrop: document.querySelector("#story-backdrop"),
  closeStory: document.querySelector("#close-story"),
  storyHelp: document.querySelector("#story-help"),
  storyContent: document.querySelector("#story-content"),
  openUpdates: document.querySelector("#open-updates"),
  updatesPanel: document.querySelector("#updates-panel"),
  updatesBackdrop: document.querySelector("#updates-backdrop"),
  closeUpdates: document.querySelector("#close-updates"),
  updatesHelp: document.querySelector("#updates-help"),
  updatesContent: document.querySelector("#updates-content"),
  updatesNotify: document.querySelector("#updates-notify"),
  helpFab: document.querySelector("#help-fab"),
  detailHelp: document.querySelector("#detail-help"),
  guidePanel: document.querySelector("#guide-panel"),
  guideBackdrop: document.querySelector("#guide-backdrop"),
  closeGuide: document.querySelector("#close-guide"),
  guideContent: document.querySelector("#guide-content"),
  guideEyebrow: document.querySelector("#guide-eyebrow"),
  guideTitle: document.querySelector("#guide-title"),
  guideSubtitle: document.querySelector("#guide-subtitle"),
  visitorWelcome: document.querySelector("#visitor-welcome"),
  detailAskAi: document.querySelector("#detail-ask-ai"),
  storyAskAi: document.querySelector("#story-ask-ai"),
  updatesAskAi: document.querySelector("#updates-ask-ai"),
  installFab: document.querySelector("#install-fab"),
  assistantFab: document.querySelector("#assistant-fab"),
  assistantPanel: document.querySelector("#assistant-panel"),
  assistantBackdrop: document.querySelector("#assistant-backdrop"),
  closeAssistant: document.querySelector("#close-assistant"),
  assistantLog: document.querySelector("#assistant-log"),
  assistantForm: document.querySelector("#assistant-form"),
  assistantInput: document.querySelector("#assistant-input"),
  assistantSend: document.querySelector("#assistant-send"),
  branchChip: document.querySelector("#branch-chip"),
  branchChipToolbar: document.querySelector("#branch-chip-toolbar"),
  branchPanel: document.querySelector("#branch-panel"),
  branchBackdrop: document.querySelector("#branch-backdrop"),
  branchContent: document.querySelector("#branch-content"),
  tabs: [...document.querySelectorAll("#tabbar [data-tab]")],
  appMenuButton: document.querySelector("#app-menu-button"),
  appMenu: document.querySelector("#app-menu"),
  detailsBack: document.querySelector("#details-back"),
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

// A person's OWN vital event: they must be the PRINCIPAL. person.events also holds
// spouse/partner-role events (a marriage, or a widow/widower named in a spouse's death
// record), which must never be read as this person's own birth or death — that is what
// made a widow show her late husband's death year as her own.
function ownEvent(person, ...types) {
  return person.events.find((event) => types.includes(event.type) && event.role === "principal");
}

function lifespan(person) {
  // Fall back to baptism/burial when the vital event itself is unrecorded, so the
  // panel header agrees with the biography prose (data-loader falls back too).
  const birth = ownEvent(person, "birth") || ownEvent(person, "baptism");
  const death = ownEvent(person, "death") || ownEvent(person, "burial");
  const birthYear = yearFromEvent(birth);
  const deathYear = yearFromEvent(death);
  if (birthYear || deathYear) return `${birthYear || "?"}–${deathYear || ""}`;
  return person.privacy === "living" ? t("lifespan.living") : t("lifespan.unknown");
}

function primaryPlace(person) {
  // The card's place line is the person's own BIRTHPLACE — their birth event, or
  // their baptism as a proxy for it. It must never fall back to a place they only
  // married or resided in: a marriage location read as a birthplace is misleading
  // (and the marriage venue is rarely where either spouse was born). Only when no
  // birth or baptism is held do we fall back to death/burial — still an own vital
  // place — and otherwise the birthplace is honestly unknown.
  const preferred = ownEvent(person, "birth")
    || ownEvent(person, "baptism")
    || ownEvent(person, "death")
    || ownEvent(person, "burial");
  return localePlace(preferred?.place?.name) || t("place.unknown");
}

// Rejected parentage edges are never drawn; every other status renders (with its
// own styling). There is no user toggle — the tree shows what has been modelled.
function relationshipVisible(relationship) {
  return relationship.status !== "rejected";
}

const firstName = (name) => String(name || "").split(" ")[0];

// Who "Relationship to …" refers to. The subject is living, so the public site withholds
// their name; say "the archive's owner" rather than print the placeholder.
function subjectLabel() {
  const subject = state.data?.people?.[SUBJECT_ID];
  return subject && subject.privacy !== "living" ? firstName(subject.name) : t("subject.owner");
}

// ---------- Family branches ----------
const chosenBranches = () =>
  state.branches ? state.branches.list.filter((branch) => !state.scope.size || state.scope.has(branch.key)) : [];
const personInScope = (personId) => !state.branches || inScope(state.branches, state.scope, personId);

// "Everything", or the chosen branches joined: "Muniz + Bohrer".
function scopeLabel(scope = state.scope) {
  if (!state.branches || !scope.size) return t("branch.everything");
  return state.branches.list.filter((branch) => scope.has(branch.key)).map((branch) => branch.label).join(" + ");
}

function branchDots(keys) {
  const dots = document.createElement("span");
  dots.className = "branch-dots";
  dots.setAttribute("aria-hidden", "true");
  for (const key of keys) {
    const dot = document.createElement("span");
    dot.className = "branch-dot";
    dot.style.setProperty("--b", state.branches.byKey[key]?.colour || "var(--muted)");
    dots.append(dot);
  }
  return dots;
}

// Small coloured tags naming the branch(es) a person, or an update, belongs to.
function branchTagsFor(keys) {
  if (!state.branches || !keys.length) return null;
  const wrap = document.createElement("span");
  wrap.className = "branch-tags";
  for (const key of keys) {
    const branch = state.branches.byKey[key];
    if (!branch) continue;
    const tag = document.createElement("span");
    tag.className = "branch-tag";
    tag.style.setProperty("--b", branch.colour);
    tag.textContent = branch.label;
    wrap.append(tag);
  }
  return wrap;
}
const branchTags = (personId) => branchTagsFor(state.branches?.personBranches[personId] || []);

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
  state.toggled.clear(); // per-card expand/collapse belongs to the previous root
  state.autoFit = true;
  if (elements.rootSelect) elements.rootSelect.value = personId;
  renderActive();
  scrollFocusIntoView();
  syncHash();
}

const SVG_NS = "http://www.w3.org/2000/svg";
const PEDIGREE_HARD_CAP = 24; // absolute generation ceiling for manual per-line expansion

// Walk the ancestry, numbering ancestors ahnentafel-style (subject k = 1, father = 2k,
// mother = 2k+1) so a father-first walk keeps the father-line left and the mother-line right;
// generation is floor(log2 k). Columns are packed afterwards (see assignColumns), not fixed at
// 2^gen, so a sparse deep line stays compact. Unknown ancestors leave a gap; the missing half of a
// partially known couple gets a faint placeholder so the symmetry reads as intentional.
function collectAhnentafel(rootId, maxGen) {
  const nodes = [];
  const unknowns = [];
  const globalSeen = new Set();

  function walk(personId, k, gen, relationship, path) {
    const person = state.data.people[personId];
    if (!person) return;
    state.visibleNodes += 1;
    const entry = { personId, k, gen, relationship, repeated: globalSeen.has(personId) && gen > 0 };
    nodes.push(entry);
    if (entry.repeated || path.has(personId)) return; // pedigree collapse / cycle guard
    globalSeen.add(personId);

    const sexOrder = { male: 0, female: 1, unknown: 2 };
    const parents = (state.data.parentsByChild[personId] || [])
      .filter(relationshipVisible)
      .sort((a, b) => {
        const sa = sexOrder[state.data.people[a.parentId]?.sex] ?? 2;
        const sb = sexOrder[state.data.people[b.parentId]?.sex] ?? 2;
        return sa !== sb
          ? sa - sb
          : (state.data.people[a.parentId]?.name || "").localeCompare(state.data.people[b.parentId]?.name || "");
      });

    // Each node is open (parents shown) or closed by default per the generation limit; a card's
    // +/- toggle flips that default, so any branch can be collapsed shut or opened past the limit.
    const defaultOpen = gen < maxGen;
    const open = state.toggled.has(personId) ? !defaultOpen : defaultOpen;
    if (!open || gen >= PEDIGREE_HARD_CAP) {
      if (parents.length && gen < PEDIGREE_HARD_CAP) entry.canOpen = true; // + : has hidden ancestry
      return;
    }
    if (!parents.length) return;
    entry.canClose = true; // - : parents are shown and can be hidden

    // Assign a stable father slot (2k) and mother slot (2k+1) by sex, falling back for unsexed or
    // single parents so a lone parent still lands in a fixed column.
    let father = parents.find((p) => state.data.people[p.parentId]?.sex === "male");
    let mother = parents.find((p) => state.data.people[p.parentId]?.sex === "female");
    const rest = parents.filter((p) => p !== father && p !== mother);
    if (!father && rest.length) father = rest.shift();
    if (!mother && rest.length) mother = rest.shift();

    const nextPath = new Set(path).add(personId);
    if (father) walk(father.parentId, 2 * k, gen + 1, father, nextPath);
    else if (mother) unknowns.push({ k: 2 * k, gen: gen + 1 });
    if (mother) walk(mother.parentId, 2 * k + 1, gen + 1, mother, nextPath);
    else if (father) unknowns.push({ k: 2 * k + 1, gen: gen + 1 });
  }

  walk(rootId, 1, 0, null, new Set());
  return { nodes, unknowns };
}

// Pack the ancestry into as few columns as it actually needs: a father-first walk gives each leaf
// the next column, and every ancestor spans its descendants' columns (so it centres over them). A
// full generation lays out evenly — the symmetric grid — while a sparse deep line collapses into a
// narrow chain instead of scattering across empty ahnentafel columns.
function assignColumns(presentKeys) {
  let nextLeaf = 0;
  const range = new Map();
  function visit(k) {
    if (!presentKeys.has(k)) return null;
    const left = visit(2 * k);
    const right = visit(2 * k + 1);
    const parts = [left, right].filter(Boolean);
    const r = parts.length
      ? [Math.min(...parts.map((p) => p[0])), Math.max(...parts.map((p) => p[1]))]
      : [nextLeaf, nextLeaf++]; // leaf: claim the next column
    range.set(k, r);
    return r;
  }
  visit(1);
  return { range, cols: nextLeaf };
}

// A +/- control under a frontier card: expand opens this ancestor's line past the base generation
// limit; collapse hides it again. Per-line, so one deep branch opens without widening the rest.
function createBranchToggle(personId, mode) {
  const collapse = mode === "collapse";
  const button = document.createElement("button");
  button.type = "button";
  button.className = `pedigree-toggle pedigree-toggle-${collapse ? "collapse" : "expand"}`;
  button.textContent = collapse ? "−" : "+";
  const label = collapse ? t("tree.collapse") : t("tree.expand");
  button.title = label;
  button.setAttribute("aria-label", label);
  button.addEventListener("click", (event) => {
    event.stopPropagation();
    // Flip this person's ancestry visibility relative to the generation-limit default.
    if (state.toggled.has(personId)) state.toggled.delete(personId);
    else state.toggled.add(personId);
    renderTree();
  });
  return button;
}

function renderTree() {
  if (!state.data) return;
  state.visibleNodes = 0;
  elements.tree.replaceChildren();
  elements.tree.classList.add("pedigree-grid");

  const root = state.data.people[state.rootId];
  if (!root) {
    elements.error.hidden = false;
    elements.error.textContent = t("tree.personUnavailable", { id: state.rootId });
    return;
  }

  const maxGen = Math.max(1, state.generations - 1);
  const { nodes, unknowns } = collectAhnentafel(state.rootId, maxGen);

  // Pack columns from the real nodes and frontier placeholders (not the theoretical 2^gen slots).
  const presentKeys = new Set([...nodes, ...unknowns].map((item) => item.k));
  const { range, cols } = assignColumns(presentKeys);

  const grid = document.createElement("div");
  grid.className = "pedigree-inner";
  grid.style.setProperty("--pedigree-cols", String(Math.max(1, cols)));

  const placeCell = (k, gen) => {
    const [minCol, maxCol] = range.get(k) || [0, 0];
    const cell = document.createElement("div");
    cell.className = "pedigree-cell";
    cell.style.gridColumn = `${minCol + 1} / ${maxCol + 2}`;
    cell.style.gridRow = String(gen + 1);
    cell.dataset.k = String(k);
    return cell;
  };

  for (const node of nodes) {
    const cell = placeCell(node.k, node.gen);
    cell.dataset.status = node.relationship?.status || "unknown";
    cell.append(
      createPersonCard(state.data.people[node.personId], node.relationship, {
        root: node.gen === 0,
        reference: node.repeated,
      }),
    );
    if (node.canOpen) cell.append(createBranchToggle(node.personId, "expand"));
    else if (node.canClose) cell.append(createBranchToggle(node.personId, "collapse"));
    grid.append(cell);
  }
  for (const slot of unknowns) {
    const cell = placeCell(slot.k, slot.gen);
    cell.classList.add("is-unknown");
    const placeholder = document.createElement("div");
    placeholder.className = "pedigree-unknown";
    placeholder.textContent = t("tree.unknownAncestor");
    cell.append(placeholder);
    grid.append(cell);
  }

  const svg = document.createElementNS(SVG_NS, "svg");
  svg.setAttribute("class", "pedigree-lines");
  grid.append(svg);

  elements.tree.append(grid);
  elements.visibleCount.textContent = String(state.visibleNodes);
  drawPedigreeLines(grid, svg, nodes);
  refreshZoom();
}

// Connect each person to its parents with an orthogonal drop, coloured by the parent edge's
// evidence tier (dashed to an unknown slot). Positions come from laid-out offsets — untouched by
// the zoom transform — so the SVG scales cleanly with the stage. A couple with a recorded marriage
// gets a badge on the junction.
function drawPedigreeLines(grid, svg, nodes) {
  // Measure the cell (its offsetParent is the positioned grid, so offsets are grid-relative;
  // the card is centred in the cell, so the cell centre is the card's connection point).
  const geo = new Map();
  grid.querySelectorAll(".pedigree-cell").forEach((cell) => {
    geo.set(Number(cell.dataset.k), {
      cx: cell.offsetLeft + cell.offsetWidth / 2,
      top: cell.offsetTop,
      bottom: cell.offsetTop + cell.offsetHeight,
      status: cell.dataset.status || "unknown",
      unknown: cell.classList.contains("is-unknown"),
    });
  });

  const width = grid.scrollWidth;
  const height = grid.scrollHeight;
  svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
  svg.setAttribute("width", String(width));
  svg.setAttribute("height", String(height));

  const nodeByK = new Map(nodes.map((node) => [node.k, node]));
  const lines = document.createDocumentFragment();
  for (const node of nodes) {
    const child = geo.get(node.k);
    if (!child) continue;
    for (const parentK of [2 * node.k, 2 * node.k + 1]) {
      const parent = geo.get(parentK);
      if (!parent) continue;
      const busY = (child.bottom + parent.top) / 2;
      const path = document.createElementNS(SVG_NS, "path");
      path.setAttribute("d", `M ${child.cx} ${child.bottom} V ${busY} H ${parent.cx} V ${parent.top}`);
      path.setAttribute("class", "pedigree-line");
      path.style.stroke = statusColours[parent.status] || statusColours.unknown;
      if (parent.unknown) path.setAttribute("stroke-dasharray", "5 5");
      lines.append(path);
    }

    // Marriage badge on the couple's junction, when both parents are modelled in one family.
    const father = nodeByK.get(2 * node.k);
    const mother = nodeByK.get(2 * node.k + 1);
    const familyId = father?.relationship?.familyId;
    if (father && mother && familyId && familyId === mother.relationship?.familyId) {
      const marriage = state.data.marriageByFamily?.[familyId];
      const fatherGeo = geo.get(2 * node.k);
      const motherGeo = geo.get(2 * node.k + 1);
      if (marriage && fatherGeo && motherGeo) {
        const badge = createMarriageBadge(marriage);
        badge.classList.add("pedigree-marriage");
        badge.style.left = `${(fatherGeo.cx + motherGeo.cx) / 2}px`;
        badge.style.top = `${(child.bottom + fatherGeo.top) / 2}px`;
        grid.append(badge);
      }
    }
  }
  svg.replaceChildren(lines);
}

function naturalSize() {
  const stage = elements.treeStage;
  return { w: stage ? stage.offsetWidth : 0, h: stage ? stage.offsetHeight : 0 };
}

function applyZoom() {
  const { w, h } = naturalSize();
  // Never zoom out past the point where the tree already fits the width — below that is
  // just empty margin. The fit floor is itself never below 25% (MIN_ZOOM).
  const floor = computeFitZoom();
  state.zoom = clamp(state.zoom, floor, MAX_ZOOM);
  elements.treeStage.style.transform = `scale(${state.zoom})`;
  elements.treeSizer.style.width = `${w * state.zoom}px`;
  elements.treeSizer.style.height = `${h * state.zoom}px`;
  elements.zoomLevel.textContent = `${Math.round(state.zoom * 100)}%`;
  elements.zoomIn.disabled = state.zoom >= MAX_ZOOM - 1e-3;
  elements.zoomOut.disabled = state.zoom <= floor + 1e-3;
}

function centerScroll() {
  const viewport = elements.treeViewport;
  viewport.scrollLeft = Math.max(0, (viewport.scrollWidth - viewport.clientWidth) / 2);
  viewport.scrollTop = 0;
}

// The zoom at which the whole tree fits the viewport width — floored at 25% (MIN_ZOOM) and
// never magnifying past 100% (FIT_MAX_ZOOM). This doubles as the zoom-out floor.
function computeFitZoom() {
  const viewport = elements.treeViewport;
  const { w } = naturalSize();
  const styles = getComputedStyle(viewport);
  const padX = parseFloat(styles.paddingLeft) + parseFloat(styles.paddingRight);
  const available = Math.max(1, viewport.clientWidth - padX);
  return clamp(w ? available / w : 1, MIN_ZOOM, FIT_MAX_ZOOM);
}

function fitZoom() {
  state.zoom = computeFitZoom();
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
  state.zoom = clamp(nextZoom, computeFitZoom(), MAX_ZOOM);
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
    branch: params.get("branch"),
  };
}

function syncHash() {
  const params = new URLSearchParams();
  params.set("root", state.rootId);
  params.set("gen", String(state.generations));
  params.set("lang", state.locale);
  if (state.branches && state.scope.size) params.set("branch", serialiseScope(state.scope, state.branches));
  if (state.selected) params.set("sel", state.selected);
  const next = `#${params.toString().replace(/%2C/g, ",")}`;
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

let searchHideTimer = null;

function hideSearchResults() {
  if (!elements.searchResults) return;
  elements.searchResults.hidden = true;
  elements.searchResults.replaceChildren();
  elements.search.setAttribute("aria-expanded", "false");
}

// Navigate to a searched person: clear the box, dismiss the list, and re-root.
function selectSearchResult(personId) {
  elements.search.value = "";
  state.searchAll = false;
  hideSearchResults();
  elements.search.blur();
  setRoot(personId);
}

// Widen or narrow the results without losing the search box (a tap on the list would
// otherwise blur it and close the list).
function setSearchAll(all) {
  clearTimeout(searchHideTimer);
  state.searchAll = all;
  renderSearchResults(elements.search.value);
  elements.search.focus();
}

function updateSearchPlaceholder() {
  if (!elements.search) return;
  elements.search.placeholder = state.scope.size
    ? t("control.searchScoped", { families: scopeLabel() })
    : t("control.searchPlaceholder");
}

// Live autocomplete, each match a tappable row; works by tap (mobile) and click/Enter
// (desktop) with no submit gesture. With families chosen, the list stays inside them and
// says how many more matches are elsewhere, one tap from showing them.
function renderSearchResults(query) {
  const box = elements.searchResults;
  if (!box || !state.data) return;
  const normalised = query.trim().toLocaleLowerCase();
  box.replaceChildren();
  if (!normalised) {
    state.searchAll = false;
    hideSearchResults();
    return;
  }
  const everyone = Object.values(state.data.people)
    .filter((person) => person.name.toLocaleLowerCase().includes(normalised))
    .sort((a, b) => a.name.localeCompare(b.name));
  if (!everyone.length) {
    hideSearchResults();
    return;
  }
  const scoped = state.scope.size ? everyone.filter((person) => personInScope(person.id)) : everyone;
  const showAll = !state.scope.size || state.searchAll;
  const matches = (showAll ? everyone : scoped).slice(0, 12);

  if (state.scope.size) {
    const switcher = document.createElement("div");
    switcher.className = "segmented search-scope";
    switcher.setAttribute("role", "group");
    for (const [all, label] of [[false, t("search.scope", { n: scoped.length })], [true, t("search.everyone", { n: everyone.length })]]) {
      const option = document.createElement("button");
      option.type = "button";
      option.textContent = label;
      option.setAttribute("aria-pressed", String(all === showAll));
      option.addEventListener("click", () => setSearchAll(all));
      switcher.append(option);
    }
    box.append(switcher);
  }
  if (!matches.length) {
    const empty = document.createElement("p");
    empty.className = "search-empty";
    empty.textContent = t("search.noneHere", { families: scopeLabel() });
    box.append(empty);
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
    const tags = branchTags(person.id);
    if (tags) item.append(tags);
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
  const elsewhere = everyone.length - scoped.length;
  if (state.scope.size && !showAll && elsewhere > 0) {
    const more = document.createElement("button");
    more.type = "button";
    more.className = "search-more";
    more.textContent = `${tn("search.more", elsewhere, { n: elsewhere })} — ${t("search.showThem")}`;
    more.addEventListener("click", () => setSearchAll(true));
    box.append(more);
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
  for (const el of document.querySelectorAll("[data-i18n-title]")) {
    el.setAttribute("title", t(el.getAttribute("data-i18n-title")));
  }
}

// --- Live visitor greeting -------------------------------------------------
// Render the cached { number, country } into #visitor-welcome in the active
// locale. Country name via Intl.DisplayNames; flag via a flagcdn image (an
// external CDN used only for the *live visitor's own* country — deliberately
// distinct from the evidence-based FLAG_SVGS used for recorded nationality).
// No-ops (stays hidden) until initVisitorWelcome has data.
function renderVisitorWelcome() {
  const el = elements.visitorWelcome;
  if (!el || !state.visitor || !state.visitor.number) return;
  const { number, country } = state.visitor;
  const code = /^[A-Za-z]{2}$/.test(country || "") ? country.toUpperCase() : null;
  const localeTag = state.locale === "pt-BR" ? "pt-BR" : "en";
  let countryName = code;
  try {
    if (code) countryName = new Intl.DisplayNames([localeTag], { type: "region" }).of(code) || code;
  } catch { /* Intl.DisplayNames unavailable — fall back to the code */ }
  const numberText = new Intl.NumberFormat(localeTag).format(number);

  // Two clauses wrapped in .visitor-part spans so narrow screens can stack them
  // onto their own centred lines (CSS) instead of wrapping mid-phrase.
  el.textContent = "";
  if (code) {
    const where = document.createElement("span");
    where.className = "visitor-part";
    where.append(t("visitor.from") + " ");
    const flag = document.createElement("img");
    flag.className = "visitor-flag";
    flag.src = `https://flagcdn.com/20x15/${code.toLowerCase()}.png`;
    flag.srcset = `https://flagcdn.com/40x30/${code.toLowerCase()}.png 2x`;
    flag.width = 20;
    flag.height = 15;
    flag.alt = "";
    flag.loading = "lazy";
    where.append(flag, " ");
    const cname = document.createElement("strong");
    cname.textContent = countryName;
    where.append(cname);
    el.append(where);
    const sep = document.createElement("span");
    sep.className = "visitor-sep";
    sep.textContent = " · ";
    el.append(sep);
  }
  const who = document.createElement("span");
  who.className = "visitor-part";
  who.append(t("visitor.number", { number: numberText }));
  el.append(who);
  el.hidden = false;
}

async function initVisitorWelcome() {
  if (!VISITOR_API || !elements.visitorWelcome) return;
  let stored = null;
  try { stored = localStorage.getItem(VISITOR_NUM_KEY); } catch { /* storage unavailable */ }
  const endpoint = VISITOR_API + (stored ? "" : "?new=1");
  try {
    const res = await fetch(endpoint, { cache: "no-store" });
    if (!res.ok) return;
    const data = await res.json();
    const number = stored ? Number(stored) : data.number;
    if (!Number.isFinite(number) || number <= 0) return;
    if (!stored) {
      try { localStorage.setItem(VISITOR_NUM_KEY, String(number)); } catch { /* ignore */ }
    }
    state.visitor = { number, country: data.country || "" };
    renderVisitorWelcome();
  } catch { /* offline, blocked, or Worker unset — leave the greeting hidden */ }
}

function setLocale(locale) {
  const next = SUPPORTED_LOCALES.includes(locale) ? locale : "en";
  state.locale = next;
  i18n = createI18n(next);
  try { localStorage.setItem(LANG_STORAGE_KEY, next); } catch { /* storage unavailable */ }
  if (elements.languageSelect) elements.languageSelect.value = next;
  applyStaticTranslations();
  renderVisitorWelcome();
  renderBranchChips();
  updateSearchPlaceholder();
  if (elements.branchPanel && !elements.branchPanel.hidden) renderBranchPanel();
  if (elements.guidePanel && !elements.guidePanel.hidden) renderGuide();
  if (elements.storyPanel && !elements.storyPanel.hidden) openStory();
  if (elements.updatesPanel && !elements.updatesPanel.hidden) openUpdates();
  refreshPushLanguage();
  // Re-localise the assistant's empty-state (its dynamic chat bubbles are left as-is), and
  // reload the AI-generated suggestions in the new language.
  assistantSuggestPool = null;
  loadAssistantSuggestions();
  if (elements.assistantPanel && !elements.assistantPanel.hidden
      && elements.assistantLog.querySelector(".assistant-empty")) renderAssistantIntro();
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
  if (returnToAssistant) { returnToAssistant = false; openAssistant(); }
}

// The "Portrait / Retrato" layer: opened from the "More details" link inside the
// biography. It docks as its OWN panel at the right edge and pushes the details panel
// left, so both stay visible side by side (no modal overlay / no dimming).
let portraitKeyHandler = null;
function closePortrait() {
  const panel = document.querySelector(".portrait-panel");
  if (panel) panel.remove();
  if (elements.detailsPanel) elements.detailsPanel.classList.remove("with-portrait");
  if (portraitKeyHandler) {
    document.removeEventListener("keydown", portraitKeyHandler);
    portraitKeyHandler = null;
  }
}
function openPortrait(person) {
  closePortrait();
  const text = localeText(person.profile, person.profilePt);
  if (!text) return;

  const panel = document.createElement("aside");
  panel.className = "portrait-panel";

  const header = document.createElement("div");
  header.className = "portrait-panel-header";
  const heading = document.createElement("div");
  heading.className = "portrait-panel-heading";
  heading.textContent = `${t("detail.portrait")} — ${person.name}`;
  const helpBtn = document.createElement("button");
  helpBtn.type = "button";
  helpBtn.className = "portrait-close portrait-help";
  helpBtn.textContent = "?";
  helpBtn.setAttribute("aria-label", t("guide.portrait.button"));
  helpBtn.title = t("guide.portrait.button");
  helpBtn.addEventListener("click", () => openGuide("portrait"));
  const closeBtn = document.createElement("button");
  closeBtn.type = "button";
  closeBtn.className = "portrait-close";
  closeBtn.textContent = "×";
  closeBtn.setAttribute("aria-label", t("reader.close"));
  closeBtn.addEventListener("click", closePortrait);
  const actions = document.createElement("div");
  actions.className = "portrait-panel-actions";
  if (ASSISTANT_API) {
    const askAiBtn = document.createElement("button");
    askAiBtn.type = "button";
    askAiBtn.className = "portrait-close portrait-help panel-ai-btn";
    askAiBtn.setAttribute("aria-label", t("assistant.fab"));
    askAiBtn.title = t("assistant.fab");
    const fabIcon = document.querySelector("#assistant-fab .assistant-fab-icon");
    if (fabIcon) askAiBtn.appendChild(fabIcon.cloneNode(true));
    askAiBtn.addEventListener("click", () => { closePortrait(); openAssistant(); });
    actions.append(askAiBtn);
  }
  actions.append(helpBtn, closeBtn);
  header.append(heading, actions);

  const body = document.createElement("div");
  body.className = "portrait portrait-panel-body";
  renderPortrait(body, text);

  panel.append(header, body);
  document.body.appendChild(panel);
  if (elements.detailsPanel) elements.detailsPanel.classList.add("with-portrait");

  portraitKeyHandler = (event) => {
    if (event.key !== "Escape") return;
    // A help overlay on top of the portrait takes Escape first.
    if (elements.guidePanel && !elements.guidePanel.hidden) return;
    closePortrait();
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
// headings, `- ` bullet lists, blank-line paragraphs, `**bold**`, `*italic*`, `---`
// rules, `[label](url)` links (Google Maps links rendered as 📍 chips), and
// [PROVEN]/[INFERRED]/[LEAD]/[CONTEXTUAL]/[DOCUMENTED]/[OPEN]/[STRONG]/[RESOLVED]/[APPROX]
// evidence tags styled as chips. Built from DOM nodes (no innerHTML).
function renderPortrait(container, text) {
  container.textContent = "";
  const inline = (parent, s) => {
    const re = /\[([^\]]+?)\]\((https?:\/\/[^)\s]+)\)|\*\*(.+?)\*\*|\*(?!\*)([^*]+?)\*|\[(PROVEN|INFERRED|LEAD|CONTEXTUAL|DOCUMENTED|OPEN|STRONG|RESOLVED|APPROX|UNLOCATED)(?:[^\]]*)?\]/g;
    let last = 0;
    let m;
    while ((m = re.exec(s)) !== null) {
      if (m.index > last) parent.appendChild(document.createTextNode(s.slice(last, m.index)));
      if (m[1] !== undefined) {
        // [label](url) → external link; Google Maps links styled as a map chip
        const a = document.createElement("a");
        a.href = m[2];
        a.target = "_blank";
        a.rel = "noopener noreferrer";
        const isMap = /(?:google\.[^/]*\/maps|maps\.google|maps\.app\.goo)/i.test(m[2]);
        a.className = isMap ? "portrait-link portrait-maplink" : "portrait-link";
        a.textContent = isMap ? "📍 " + m[1] : m[1];
        parent.appendChild(a);
      } else if (m[3] !== undefined) {
        const b = document.createElement("strong");
        b.textContent = m[3];
        parent.appendChild(b);
      } else if (m[4] !== undefined) {
        const em = document.createElement("em");
        em.textContent = m[4];
        parent.appendChild(em);
      } else {
        const span = document.createElement("span");
        span.className = "tier tier-" + m[5].toLowerCase();
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
    else para.appendChild(document.createTextNode(" "));
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

// A scrollable multi-page gallery for a document held as several page images (or
// PDFs), each page labelled. The column scrolls on desktop and mobile so every
// page of a multi-page document is reachable, not just the first.
function pagesGallery(pages, label) {
  const wrap = document.createElement("div");
  wrap.className = "reader-image-pane reader-gallery";
  pages.forEach((page, index) => {
    const fig = document.createElement("figure");
    fig.className = "reader-page";
    const cap = document.createElement("figcaption");
    cap.className = "reader-page-label";
    cap.textContent = t("reader.page", { n: index + 1, total: pages.length });
    fig.appendChild(cap);
    if (page.fileType === "pdf") {
      const frame = document.createElement("iframe");
      frame.className = "reader-page-pdf";
      frame.src = page.url;
      frame.title = label || "";
      fig.appendChild(frame);
    } else {
      const img = document.createElement("img");
      img.className = "reader-page-img";
      img.src = page.url;
      img.alt = "";
      img.loading = "lazy";
      img.draggable = false;
      fig.appendChild(img);
    }
    wrap.appendChild(fig);
  });
  return wrap;
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
  heading.append(hid, document.createTextNode(localeText(source.title, source.titlePt) || source.id));
  const closeBtn = document.createElement("button");
  closeBtn.type = "button";
  closeBtn.className = "reader-close";
  closeBtn.textContent = "✕";
  closeBtn.setAttribute("aria-label", t("reader.close"));
  closeBtn.addEventListener("click", closeReader);
  const headerBtns = document.createElement("div");
  headerBtns.className = "reader-header-btns";
  if (ASSISTANT_API) {
    const readerAskAi = document.createElement("button");
    readerAskAi.type = "button";
    readerAskAi.className = "reader-close reader-ask-ai panel-ai-btn";
    readerAskAi.setAttribute("aria-label", t("assistant.fab"));
    readerAskAi.title = t("assistant.fab");
    const fabIcon = document.querySelector("#assistant-fab .assistant-fab-icon");
    if (fabIcon) readerAskAi.appendChild(fabIcon.cloneNode(true));
    readerAskAi.addEventListener("click", () => { closeReader(); openAssistant(); });
    headerBtns.append(readerAskAi);
  }
  headerBtns.append(closeBtn);
  header.append(heading, headerBtns);

  const body = document.createElement("div");
  body.className = "reader-body";
  let leftPane;
  if (Array.isArray(source.pages) && source.pages.length > 1) {
    leftPane = pagesGallery(source.pages, localeText(source.title, source.titlePt) || source.id);
  } else if (source.fileType === "pdf") {
    leftPane = document.createElement("iframe");
    leftPane.className = "reader-pdf";
    leftPane.src = source.file;
    leftPane.title = localeText(source.title, source.titlePt) || source.id;
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

function sourceList(sources) {
  if (!sources.length) {
    const empty = document.createElement("p");
    empty.className = "empty-note";
    empty.textContent = t("empty.sources");
    return empty;
  }

  // `person.sources` already arrives ordered by the owner-defined FONTES rule
  // (data-loader.js): the person's OWN records first, by vital type (birth/baptism →
  // marriage → death), then the vital certificates that only MENTION them, then all
  // other context last. Render in that order — do NOT re-sort by record type here, or a
  // certificate that merely mentions the person (e.g. a child's birth record) would jump
  // ahead of their own marriage and death records.
  const sorted = sources;

  // Sub-group headings, driven by the explicit `group` label the data-loader
  // attaches to each source (own / mention / context). Only shown when the
  // person's sources actually span more than one group, so a person with a
  // single group keeps a clean, unlabelled list under the "Sources" heading.
  const GROUP_LABELS = {
    own: t("source.group.own"),
    mention: t("source.group.mention"),
    context: t("source.group.context"),
  };
  const groupsPresent = new Set(sorted.map((source) => source.group).filter(Boolean));
  const showGroupHeaders = groupsPresent.size > 1;
  let lastGroup = null;

  const ul = document.createElement("ul");
  ul.className = "source-list";

  for (const source of sorted) {
    if (showGroupHeaders && source.group && source.group !== lastGroup) {
      lastGroup = source.group;
      const groupHeader = document.createElement("li");
      groupHeader.className = "source-group-title";
      groupHeader.setAttribute("role", "presentation");
      groupHeader.textContent = GROUP_LABELS[source.group] || "";
      ul.append(groupHeader);
    }

    const li = document.createElement("li");
    li.className = source.uncertain ? "source-item source-flagged" : "source-item";

    const title = document.createElement("div");
    title.className = "source-title";
    const id = document.createElement("span");
    id.className = "source-id";
    id.textContent = source.id;
    title.append(id, document.createTextNode(localeText(source.title, source.titlePt) || source.id));

    const metaBits = [
      source.recordCategory && vocab("recordCategory", source.recordCategory),
      source.sourceForm && vocab("sourceForm", source.sourceForm),
      source.quality && vocab("quality", source.quality),
    ].filter(Boolean);
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
    title.append(id, document.createTextNode(localeText(ref.title, ref.titlePt) || ref.id));

    const metaBits = [
      ref.role,
      ref.recordCategory && vocab("recordCategory", ref.recordCategory),
      localePlace(ref.place),
    ].filter(Boolean);
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
  const tags = branchTags(person.id);
  if (tags) elements.detailsLifespan.append(" ", tags);
  elements.detailsContent.replaceChildren();

  if (person.hasConflict) {
    const caution = document.createElement("p");
    caution.className = "detail-caution";
    caution.textContent = t("detail.caution");
    elements.detailsContent.append(caution);
  }

  const bio = biographyParagraph(person);
  let moreWrap = null;
  if (localeText(person.profile, person.profilePt)) {
    moreWrap = document.createElement("div");
    moreWrap.className = "portrait-more";
    const moreBtn = document.createElement("button");
    moreBtn.type = "button";
    moreBtn.className = "portrait-more-btn";
    moreBtn.textContent = t("detail.moreDetails");
    moreBtn.addEventListener("click", () => openPortrait(person));
    moreWrap.appendChild(moreBtn);
  }
  if (bio) {
    // The "More details" link lives INSIDE the Biography section (above its rule).
    const bioWrap = document.createElement("div");
    bioWrap.append(bio);
    if (moreWrap) bioWrap.append(moreWrap);
    elements.detailsContent.append(section(t("detail.biography"), bioWrap));
  } else if (moreWrap) {
    elements.detailsContent.append(section(t("detail.biography"), moreWrap));
  }

  const relationship = relationshipContent(person);
  if (relationship) {
    elements.detailsContent.append(section(t("detail.relationship", { name: subjectLabel() }), relationship));
  }

  const facts = document.createElement("dl");
  facts.className = "detail-grid";
  const factRows = [
    [t("fact.privacy"), vocab("privacy", person.privacy)],
    [t("fact.sources"), String(person.sourceCount)],
    [t("fact.contextRefs"), String((person.fanReferences || []).length)],
    // Birthplace falls back to the person's own baptism place when no birth event is
    // held — for pre-registration ancestors the baptism parish is the birthplace.
    // ownEvent() requires the principal role, so a spouse's role in a death record or a
    // parent's role in a child's baptism never leaks here. Death falls back to burial.
    [t("fact.birthplace"), localePlace((ownEvent(person, "birth") || ownEvent(person, "baptism"))?.place?.name) || t("value.notEstablished")],
    [t("fact.nationality"), nationalityValue(person.nationality)],
    [t("fact.deathplace"), localePlace((ownEvent(person, "death") || ownEvent(person, "burial"))?.place?.name) || t("value.notEstablished")],
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

    const storyLink = document.createElement("button");
    storyLink.type = "button";
    storyLink.className = "story-link";
    storyLink.textContent = t("detail.readStory");
    storyLink.addEventListener("click", () => { closeDetails(); openStory(); });
    elements.detailsContent.append(section(t("control.story"), storyLink));
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

// The "Family Story" reading page — the long-form convergence narrative, stored as
// literal-scalar (|-) markdown in ./family-story.yaml (en / pt) so it stays
// repo-standard YAML with its paragraph breaks and wraps preserved, and rendered
// with the same light-markdown renderer as the portraits. Fetched once, cached.
let storyDoc = null;
async function loadStory(locale) {
  if (!storyDoc) {
    const response = await fetch("./family-story.yaml", { cache: "no-store" });
    if (!response.ok) throw new Error(String(response.status));
    storyDoc = parseYaml(await response.text());
  }
  return storyDoc[locale === "pt-BR" ? "pt" : "en"] || storyDoc.en || "";
}

async function openStory() {
  if (!elements.storyPanel) return;
  closeUpdates();
  const opening = elements.storyPanel.hidden;
  elements.storyPanel.hidden = false;
  elements.storyBackdrop.hidden = false;
  if (opening && !elements.storyPanel.contains(document.activeElement)) {
    lastFocused = document.activeElement;
  }
  elements.storyContent.textContent = t("story.loading");
  if (opening) elements.closeStory.focus();
  try {
    const text = await loadStory(state.locale);
    // The story is written as four rivers; a reader following some families gets theirs first.
    const rivers = state.scope.size && !state.storyFullOrder ? chosenBranches().map((branch) => branch.river) : [];
    renderPortrait(elements.storyContent, rivers.length ? reorderStory(text, rivers) : text);
    if (state.scope.size) elements.storyContent.prepend(storyScopeNote());
    if (opening) elements.storyContent.scrollTop = 0;
  } catch {
    elements.storyContent.textContent = t("story.error");
  }
}

function storyScopeNote() {
  const note = document.createElement("div");
  note.className = "story-scope-note";
  if (!state.storyFullOrder) {
    const text = document.createElement("p");
    text.textContent = t("story.scopedNote", { families: scopeLabel() });
    note.append(text);
  }
  const toggle = document.createElement("button");
  toggle.type = "button";
  toggle.className = "update-chip";
  toggle.textContent = state.storyFullOrder ? t("story.scopedOrder", { families: scopeLabel() }) : t("story.fullOrder");
  toggle.addEventListener("click", () => {
    state.storyFullOrder = !state.storyFullOrder;
    openStory().then(() => { elements.storyPanel.scrollTop = 0; });
  });
  note.append(toggle);
  return note;
}

function closeStory() {
  if (!elements.storyPanel) return;
  elements.storyPanel.hidden = true;
  elements.storyBackdrop.hidden = true;
  if (lastFocused && lastFocused.isConnected && typeof lastFocused.focus === "function") {
    lastFocused.focus();
  }
  lastFocused = null;
}

// AI family-history assistant — a chat overlay backed by the family-assistant Worker
// (workers/family-assistant/). Questions are answered strictly from this archive's
// data and streamed back token by token. Dormant unless ASSISTANT_API is set.
let assistantBusy = false;
// Set when the user clicks an entity link inside an answer: closing the person/document
// they jumped to then reopens the chat (with its history intact).
let returnToAssistant = false;
// AI-generated example questions fetched from the Worker (null until loaded; falls back to
// the curated i18n pool).
let assistantSuggestPool = null;

function openAssistant() {
  if (!elements.assistantPanel) return;
  const opening = elements.assistantPanel.hidden;
  if (opening && !elements.assistantPanel.contains(document.activeElement)) {
    lastFocused = document.activeElement;
  }
  // Close the sibling reading panels (the guide layers above and is left alone).
  if (elements.storyPanel) { elements.storyPanel.hidden = true; elements.storyBackdrop.hidden = true; }
  if (elements.updatesPanel) { elements.updatesPanel.hidden = true; elements.updatesBackdrop.hidden = true; }
  elements.assistantPanel.hidden = false;
  elements.assistantBackdrop.hidden = false;
  if (!elements.assistantLog.querySelector(".assistant-msg")) renderAssistantIntro();
  if (opening && elements.assistantInput) elements.assistantInput.focus();
}

function closeAssistant() {
  if (!elements.assistantPanel) return;
  elements.assistantPanel.hidden = true;
  elements.assistantBackdrop.hidden = true;
  if (lastFocused && lastFocused.isConnected && typeof lastFocused.focus === "function") {
    lastFocused.focus();
  }
  lastFocused = null;
}

// Build a pool of context-specific questions when a person's details panel is open.
// Picks templates that apply to the person's actual data (skips e.g. "Who were X's
// children?" when they have none), then shuffles and returns up to 6.
function personContextQuestions(person) {
  const name = person.name;
  const firstName = name.split(" ")[0];
  const rootPerson = state.data?.people[state.rootId];
  // A living root's name is withheld on the public site — no "related to Private?" question.
  const rootFirst = rootPerson && rootPerson.id !== person.id && rootPerson.privacy !== "living"
    ? firstName(rootPerson.name)
    : null;
  const repl = (key, extra) => {
    let s = t(key).replace("{name}", firstName);
    if (extra) s = s.replace("{root}", extra);
    return s;
  };

  const pool = [];
  pool.push(repl("assistant.ctx.about"));
  if (rootFirst) pool.push(repl("assistant.ctx.relation", rootFirst));
  if ((state.data?.parentsByChild[person.id] || []).length) pool.push(repl("assistant.ctx.parents"));
  if ((person.children || []).length) pool.push(repl("assistant.ctx.children"));
  if ((person.spouses || []).length) pool.push(repl("assistant.ctx.marriage"));
  if ((person.occupations || []).length) pool.push(repl("assistant.ctx.occupation"));
  if ((person.siblings || []).length) pool.push(repl("assistant.ctx.siblings"));
  if ((person.sources || []).length) pool.push(repl("assistant.ctx.documents"));
  if (person.profile || person.profilePt) pool.push(repl("assistant.ctx.portrait"));
  pool.push(repl("assistant.ctx.origin"));

  for (let i = pool.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [pool[i], pool[j]] = [pool[j], pool[i]];
  }
  return pool.slice(0, 6);
}

// The empty-state: a one-line prompt plus a few tappable example questions.
// When the user has a person's details panel open, the questions are tailored to that
// person; otherwise falls back to the AI-generated pool or the curated i18n set.
function renderAssistantIntro() {
  const log = elements.assistantLog;
  if (!log) return;
  log.textContent = "";
  const wrap = document.createElement("div");
  wrap.className = "assistant-empty";

  // Emblem — reuse the "Ask" pill's chat glyph so the empty state feels part of the brand.
  const icon = document.createElement("div");
  icon.className = "assistant-empty-icon";
  const fabIcon = document.querySelector("#assistant-fab .assistant-fab-icon");
  if (fabIcon) icon.appendChild(fabIcon.cloneNode(true));
  wrap.append(icon);

  // Context: if a person panel is open alongside the assistant, tailor everything to them.
  const ctxPerson = (state.selected && elements.detailsPanel && !elements.detailsPanel.hidden)
    ? state.data?.people[state.selected]
    : null;
  const ctxFirst = ctxPerson ? ctxPerson.name.split(" ")[0] : null;

  const intro = document.createElement("p");
  intro.className = "assistant-empty-lead";
  intro.textContent = ctxPerson
    ? t("assistant.ctx.intro").replace("{name}", ctxFirst)
    : t("assistant.intro");
  wrap.append(intro);

  const label = document.createElement("p");
  label.className = "assistant-empty-label";
  label.textContent = ctxPerson
    ? t("assistant.ctx.label").replace("{name}", ctxFirst)
    : t("assistant.suggestLabel");
  wrap.append(label);

  const suggest = document.createElement("div");
  suggest.className = "assistant-suggest";

  let items;
  if (ctxPerson) {
    items = personContextQuestions(ctxPerson);
  } else {
    // Prefer the AI-generated pool fetched from the Worker (fresh per data version); fall back
    // to the curated 12. Show 6 at random, so each fresh page/open surfaces a new set.
    items = (assistantSuggestPool && assistantSuggestPool.length >= 6)
      ? [...assistantSuggestPool]
      : Array.from({ length: 12 }, (_, i) => t(`assistant.q${i + 1}`));
    for (let i = items.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [items[i], items[j]] = [items[j], items[i]];
    }
    items = items.slice(0, 6);
  }

  for (const q of items) {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "assistant-suggest-item";
    b.textContent = q;
    b.addEventListener("click", () => {
      elements.assistantInput.value = q;
      submitAssistant();
    });
    suggest.append(b);
  }
  wrap.append(suggest);
  log.append(wrap);
}

// Fetch a pool of AI-generated example questions for the current language (cached in the
// Worker per data version). On success, later renders of the empty state draw from it; on
// failure the curated 12 in i18n remain the fallback.
async function loadAssistantSuggestions() {
  if (!ASSISTANT_API) return;
  const lang = state.locale === "pt-BR" ? "pt" : "en";
  try {
    const res = await fetch(`${ASSISTANT_API}/suggest`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ lang }),
    });
    if (!res.ok) return;
    const data = await res.json();
    if (Array.isArray(data.questions) && data.questions.length >= 6) {
      assistantSuggestPool = data.questions;
      // If the empty state is on screen right now, refresh it with the richer pool.
      if (elements.assistantPanel && !elements.assistantPanel.hidden
          && elements.assistantLog && elements.assistantLog.querySelector(".assistant-empty")) {
        renderAssistantIntro();
      }
    }
  } catch { /* keep the curated fallback */ }
}

function appendAssistantMessage(role, text) {
  const el = document.createElement("div");
  el.className = `assistant-msg ${role}`;
  el.textContent = text || "";
  elements.assistantLog.append(el);
  elements.assistantLog.scrollTop = elements.assistantLog.scrollHeight;
  return el;
}

function setAssistantBusy(busy) {
  assistantBusy = busy;
  if (elements.assistantSend) {
    elements.assistantSend.disabled = busy;
    elements.assistantSend.textContent = busy ? t("assistant.sending") : t("assistant.send");
  }
}

function autoGrowAssistantInput() {
  const ta = elements.assistantInput;
  if (!ta) return;
  ta.style.height = "auto";
  ta.style.height = Math.min(ta.scrollHeight, 128) + "px";
}

// Send the current question to the Worker and stream the plain-text reply into a
// bot bubble. One question at a time (guarded by assistantBusy).
async function submitAssistant() {
  if (assistantBusy || !ASSISTANT_API || !elements.assistantInput) return;
  const question = elements.assistantInput.value.trim();
  if (!question) return;

  const intro = elements.assistantLog.querySelector(".assistant-empty");
  if (intro) intro.remove();
  appendAssistantMessage("user", question);
  elements.assistantInput.value = "";
  autoGrowAssistantInput();
  setAssistantBusy(true);

  // Pending bubble with a live "searching the records" label (the CSS adds the animated
  // dots) so the user always sees progress, never a dead spinner.
  const bot = appendAssistantMessage("bot", t("assistant.searching"));
  bot.classList.add("pending");
  elements.assistantLog.scrollTop = elements.assistantLog.scrollHeight;

  // Hard client timeout so the UI can never appear frozen: if the Worker or model stalls,
  // abort and tell the user to retry rather than spinning forever.
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 40000);
  try {
    const res = await fetch(ASSISTANT_API, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, lang: state.locale === "pt-BR" ? "pt" : "en", viewer: getViewerKey() }),
      signal: controller.signal,
    });
    const data = await res.json().catch(() => ({}));
    bot.classList.remove("pending");
    if (res.ok && data.answer && data.answer.trim()) {
      // If the Worker auto-detected a viewer from a self-introduction, persist it for
      // the rest of the session so all follow-up questions stay personalised.
      if (data.detectedViewer && !sessionViewerKey) sessionViewerKey = data.detectedViewer;
      // Render the answer's markdown (bold names, italic source-forms, bullet lists,
      // headings) with the same safe DOM renderer the profiles/story use, then turn
      // entity IDs (people, documents) into clickable navigation links.
      renderPortrait(bot, data.answer.trim());
      linkifyAssistant(bot);
      linkifyAssistantNames(bot);
    } else {
      bot.classList.add("error");
      bot.textContent = t("assistant.error");
    }
  } catch (err) {
    bot.classList.remove("pending");
    bot.classList.add("error");
    bot.textContent = err && err.name === "AbortError" ? t("assistant.timeout") : t("assistant.error");
  } finally {
    clearTimeout(timeout);
    setAssistantBusy(false);
    elements.assistantLog.scrollTop = elements.assistantLog.scrollHeight;
    if (elements.assistantPanel && !elements.assistantPanel.hidden) elements.assistantInput.focus();
  }
}

// Resolve an entity id mentioned in an answer to a navigation action, or null if it
// cannot be routed (an event/family id, or a private/absent entity). Clicking closes the
// assistant and opens the target; reopening the "Ask" pill restores the conversation.
function resolveAssistantLink(id) {
  if (/^P-\d{3,4}$/.test(id)) {
    const person = state.data && state.data.people && state.data.people[id];
    if (!person) return null;
    return () => { returnToAssistant = true; closeAssistant(); openDetails(id); };
  }
  if (/^(?:CIV|GOV|PAR|PRB|NWS|PUB|REC)-\d{3,4}$/.test(id)) {
    const source = state.data && state.data.sources && state.data.sources[id];
    if (!source) return null;
    return () => { returnToAssistant = true; closeAssistant(); openReader(source); };
  }
  return null;
}

// Normalize a name for matching: strip accents, lowercase, collapse whitespace.
function normAssistName(s) {
  return s.normalize("NFKD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/\s+/g, " ").trim();
}

// Lazily build a preferred-name → person-id map from the loaded tree (deceased only),
// so a **bold name** in an answer becomes a link to that person even when the answer
// carries no P-#### id for them.
let assistantNameMap = null;
function getAssistantNameMap() {
  if (assistantNameMap) return assistantNameMap;
  assistantNameMap = new Map();
  const people = (state.data && state.data.people) || {};
  for (const [id, p] of Object.entries(people)) {
    if (!p || !p.name || p.privacy === "living") continue;
    const key = normAssistName(p.name);
    if (key && !assistantNameMap.has(key)) assistantNameMap.set(key, id);
  }
  return assistantNameMap;
}

// Turn a rendered bold/italic person name into a link to that person's panel.
function linkifyAssistantNames(root) {
  const map = getAssistantNameMap();
  for (const el of root.querySelectorAll("strong, em")) {
    if (el.closest("button, a")) continue;
    const id = map.get(normAssistName(el.textContent || ""));
    if (!id) continue;
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "assistant-ref assistant-ref-name";
    btn.addEventListener("click", () => { returnToAssistant = true; closeAssistant(); openDetails(id); });
    el.parentNode.replaceChild(btn, el);
    btn.appendChild(el); // keep the original bold/italic styling inside the link
  }
}

const ASSISTANT_ID_RE = /\b(P-\d{3,4}|(?:CIV|GOV|PAR|PRB|NWS|PUB|REC)-\d{3,4})\b/g;

// Walk the rendered answer's text nodes and turn each navigable entity id into a
// clickable link, leaving unroutable ids (events, families, absent people) as plain text.
function linkifyAssistant(root) {
  const nodes = [];
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  while (walker.nextNode()) nodes.push(walker.currentNode);
  for (const node of nodes) {
    const text = node.nodeValue;
    ASSISTANT_ID_RE.lastIndex = 0;
    if (!ASSISTANT_ID_RE.test(text)) continue;
    if (node.parentElement && node.parentElement.closest("a, button")) continue;
    const frag = document.createDocumentFragment();
    let last = 0;
    let m;
    ASSISTANT_ID_RE.lastIndex = 0;
    while ((m = ASSISTANT_ID_RE.exec(text)) !== null) {
      if (m.index > last) frag.appendChild(document.createTextNode(text.slice(last, m.index)));
      const open = resolveAssistantLink(m[1]);
      if (open) {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "assistant-ref";
        btn.textContent = m[1];
        btn.addEventListener("click", open);
        frag.appendChild(btn);
      } else {
        frag.appendChild(document.createTextNode(m[0]));
      }
      last = m.index + m[0].length;
    }
    if (last < text.length) frag.appendChild(document.createTextNode(text.slice(last)));
    node.parentNode.replaceChild(frag, node);
  }
}

// The "How to explore" guide — a family-facing, navigation-first help overlay. It
// opens once automatically on a first visit (flagged in localStorage) and any time
// the "? Help" button is tapped. Content is built here from i18n keys so it stays
// bilingual and in step with the actual controls; the panel reuses the Family Story
// styling (centred card on desktop, full-screen sheet on mobile).

// One numbered "how to" step: a gold chip + a title and body. `body` is chosen per
// layout by the caller so the wording matches what the user can actually do.
function guideStep(num, title, body) {
  const step = document.createElement("div");
  step.className = "guide-step";
  const chip = document.createElement("span");
  chip.className = "guide-step-num";
  chip.setAttribute("aria-hidden", "true");
  chip.textContent = String(num);
  const text = document.createElement("div");
  text.className = "guide-step-text";
  const h = document.createElement("p");
  h.className = "guide-step-title";
  h.textContent = title;
  const p = document.createElement("p");
  p.className = "guide-step-body";
  p.textContent = body;
  text.append(h, p);
  step.append(chip, text);
  return step;
}

// The guide serves two topics from one panel: "nav" (how to move around the tree,
// opened from the floating "?" / the mobile nav) and "card" (what each part of the
// open person panel means, opened from the panel's own "?").
let guideTopic = "nav";

function setGuideHead(eyebrow, title, subtitle) {
  if (elements.guideEyebrow) elements.guideEyebrow.textContent = eyebrow;
  if (elements.guideTitle) elements.guideTitle.textContent = title;
  if (elements.guideSubtitle) elements.guideSubtitle.textContent = subtitle;
}

// A term → explanation row, used by the "About this card" help to name each part
// of the person panel.
function guideDef(label, body) {
  const row = document.createElement("div");
  row.className = "guide-def";
  const l = document.createElement("p");
  l.className = "guide-def-label";
  l.textContent = label;
  const b = document.createElement("p");
  b.className = "guide-def-body";
  b.textContent = body;
  row.append(l, b);
  return row;
}

// A def whose body is followed by a small nested list — used for Sources, to name
// the panel's three sub-groups (own / mention / context) with a one-line gloss each,
// reusing the exact sub-header labels so the help and the panel read identically.
function guideDefWithGroups(label, intro, groups) {
  const row = guideDef(label, intro);
  const ul = document.createElement("ul");
  ul.className = "guide-def-groups";
  for (const [groupLabel, groupBody] of groups) {
    const li = document.createElement("li");
    const strong = document.createElement("strong");
    strong.textContent = groupLabel;
    li.append(strong, document.createTextNode(` — ${groupBody}`));
    ul.append(li);
  }
  row.append(ul);
  return row;
}

// The navigation guide — how to move around the tree (layout-aware).
function renderGuideNav(container, name) {
  const mobile = isMobile();
  const intro = document.createElement("p");
  intro.className = "guide-intro";
  intro.textContent = t("guide.intro");
  container.append(intro);

  const steps = document.createElement("div");
  steps.className = "guide-steps";
  const rows = [
    [t("guide.families.title"), mobile ? t("guide.families.mobile") : t("guide.families.desktop")],
    [t("guide.move.title"), mobile ? t("guide.move.mobile") : t("guide.move.desktop")],
    [t("guide.home.title"), (mobile ? t("guide.home.mobile") : t("guide.home.desktop")).replace("{name}", name)],
    [t("guide.search.title"), t("guide.search.body")],
    [t("guide.records.title"), mobile ? t("guide.records.mobile") : t("guide.records.desktop")],
  ];
  if (mobile) rows.push([t("guide.tabs.title"), t("guide.tabs.body")]);
  if (ASSISTANT_API) rows.push([t("guide.ai.title"), mobile ? t("guide.ai.body.mobile") : t("guide.ai.body.desktop")]);
  rows.forEach(([title, body], index) => steps.append(guideStep(index + 1, title, body)));
  container.append(steps);

  // Legend — the few glyphs a lay reader cannot decode: the birthplace flag, the
  // evidence-tier edge colour, and the record badges.
  const legend = document.createElement("div");
  legend.className = "guide-legend";
  const legendTitle = document.createElement("p");
  legendTitle.className = "guide-legend-title";
  legendTitle.textContent = t("guide.legend.title");
  legend.append(legendTitle);

  const flagRow = document.createElement("p");
  flagRow.className = "guide-legend-row";
  flagRow.append(document.createTextNode("🏳️ "), document.createTextNode(t("guide.legend.flag")));
  legend.append(flagRow);

  const tierRow = document.createElement("p");
  tierRow.className = "guide-legend-row";
  tierRow.append(document.createTextNode(`${t("guide.legend.tiers")} `));
  [
    ["confirmed", t("guide.legend.confirmed")],
    ["strong-evidence", t("guide.legend.strong")],
    ["hypothesis", t("guide.legend.hypothesis")],
  ].forEach(([status, label], i) => {
    if (i > 0) tierRow.append(document.createTextNode(" · "));
    const swatch = document.createElement("span");
    swatch.className = "guide-swatch";
    swatch.style.background = statusColours[status];
    swatch.setAttribute("aria-hidden", "true");
    tierRow.append(swatch, document.createTextNode(` ${label}`));
  });
  tierRow.append(document.createTextNode("."));
  legend.append(tierRow);

  const badgeRow = document.createElement("p");
  badgeRow.className = "guide-legend-row";
  badgeRow.textContent = t("guide.legend.badges");
  legend.append(badgeRow);
  container.append(legend);

  // "Save as an app" tip — shown on mobile, hidden if already running as PWA.
  const standalone = window.matchMedia("(display-mode: standalone)").matches || navigator.standalone;
  const isIos = /iphone|ipad|ipod/i.test(navigator.userAgent) && !window.MSStream;
  const isAndroid = /android/i.test(navigator.userAgent);
  if (!standalone && (isIos || isAndroid)) {
    const installBox = document.createElement("div");
    installBox.className = "guide-legend guide-install-tip";
    const installTitle = document.createElement("p");
    installTitle.className = "guide-legend-title";
    installTitle.textContent = t("guide.install.title");
    const installBody = document.createElement("p");
    installBody.className = "guide-legend-row";
    installBody.textContent = t("guide.install.body");
    const installHint = document.createElement("p");
    installHint.className = "guide-legend-row";
    installHint.textContent = isIos ? t("guide.install.ios") : t("guide.install.android");
    installBox.append(installTitle, installBody, installHint);
    container.append(installBox);
  }
}

// The "About this portrait" help — explains the in-depth research narrative and
// its notation (evidence tags, source codes). Kept balanced: a short intro + a few
// rows, not a manual.
function renderGuidePortrait(container) {
  const intro = document.createElement("p");
  intro.className = "guide-intro";
  intro.textContent = t("guide.portrait.intro");
  container.append(intro);

  const defs = document.createElement("div");
  defs.className = "guide-defs";
  defs.append(
    guideDefWithGroups(t("guide.portrait.tags.label"), t("guide.portrait.tags.body"), [
      ["[PROVEN]", t("guide.portrait.tag.proven")],
      ["[STRONG-EVIDENCE]", t("guide.portrait.tag.strong")],
      ["[INFERRED]", t("guide.portrait.tag.inferred")],
      ["[LEAD]", t("guide.portrait.tag.lead")],
      ["[OPEN]", t("guide.portrait.tag.open")],
    ]),
    guideDefWithGroups(t("guide.portrait.sources.label"), t("guide.portrait.sources.body"), [
      ["CIV", t("guide.portrait.src.civ")],
      ["PAR", t("guide.portrait.src.par")],
      ["PRB", t("guide.portrait.src.prb")],
      ["GOV", t("guide.portrait.src.gov")],
      ["NWS", t("guide.portrait.src.nws")],
      ["PUB", t("guide.portrait.src.pub")],
      ["REC", t("guide.portrait.src.rec")],
    ]),
    guideDef(t("guide.portrait.sections.label"), t("guide.portrait.sections.body")),
    guideDef(t("guide.portrait.maps.label"), t("guide.portrait.maps.body")),
    guideDef(t("guide.portrait.vs.label"), t("guide.portrait.vs.body")),
  );
  container.append(defs);
}

// The "About this card" help — names each section of the open person panel.
function renderGuideCard(container, name) {
  const intro = document.createElement("p");
  intro.className = "guide-intro";
  intro.textContent = t("guide.card.intro");
  container.append(intro);

  const defs = document.createElement("div");
  defs.className = "guide-defs";
  defs.append(
    guideDef(t("guide.card.bio.label"), t("guide.card.bio.body")),
    guideDef(t("guide.card.rel.label"), t("guide.card.rel.body").replace("{name}", name)),
    guideDef(t("guide.card.overview.label"), t("guide.card.overview.body")),
    guideDef(t("guide.card.events.label"), t("guide.card.events.body")),
    guideDef(t("guide.card.family.label"), t("guide.card.family.body")),
    guideDefWithGroups(t("guide.card.sources.label"), t("guide.card.sources.body"), [
      [t("source.group.own"), t("guide.card.sources.own")],
      [t("source.group.mention"), t("guide.card.sources.mention")],
      [t("source.group.context"), t("guide.card.sources.context")],
    ]),
    guideDef(t("guide.card.caution.label"), t("guide.card.caution.body")),
  );
  container.append(defs);
}

// Simple intro + term/explanation list, shared by the "About what's new" and
// "About the family story" panel-help topics.
function renderGuideDefs(container, introKey, rows) {
  const intro = document.createElement("p");
  intro.className = "guide-intro";
  intro.textContent = t(introKey);
  container.append(intro);
  const defs = document.createElement("div");
  defs.className = "guide-defs";
  for (const [labelKey, bodyKey] of rows) defs.append(guideDef(t(labelKey), t(bodyKey)));
  container.append(defs);
}

function renderGuide() {
  const container = elements.guideContent;
  if (!container) return;
  container.replaceChildren();
  const name = subjectLabel();
  if (guideTopic === "card") {
    setGuideHead(t("guide.card.eyebrow"), t("guide.card.title"), t("guide.card.subtitle"));
    renderGuideCard(container, name);
  } else if (guideTopic === "portrait") {
    setGuideHead(t("guide.portrait.eyebrow"), t("guide.portrait.title"), t("guide.portrait.subtitle"));
    renderGuidePortrait(container);
  } else if (guideTopic === "updates") {
    setGuideHead(t("guide.updates.eyebrow"), t("guide.updates.title"), t("guide.updates.subtitle"));
    renderGuideDefs(container, "guide.updates.intro", [
      ["guide.updates.what.label", "guide.updates.what.body"],
      ["guide.updates.open.label", "guide.updates.open.body"],
      ["guide.updates.privacy.label", "guide.updates.privacy.body"],
      ["guide.updates.notify.label", "guide.updates.notify.body"],
    ]);
  } else if (guideTopic === "story") {
    setGuideHead(t("guide.story.eyebrow"), t("guide.story.title"), t("guide.story.subtitle"));
    renderGuideDefs(container, "guide.story.intro", [
      ["guide.story.grounded.label", "guide.story.grounded.body"],
      ["guide.story.living.label", "guide.story.living.body"],
      ["guide.story.links.label", "guide.story.links.body"],
    ]);
  } else {
    setGuideHead(t("guide.eyebrow"), t("guide.title"), t("guide.subtitle"));
    renderGuideNav(container, name);
  }

  const gotit = document.createElement("button");
  gotit.type = "button";
  gotit.className = "guide-gotit";
  gotit.textContent = t("guide.gotit");
  gotit.addEventListener("click", closeGuide);
  container.append(gotit);
}

// Show the floating "?" only on the bare tree/focus view — hide it whenever any
// modal overlay is open (each uses a `.panel-backdrop`), so it never floats over a
// dimmed panel. Driven by a MutationObserver on the backdrops (see bindEvents), so
// it stays correct without touching every open/close path.
// The beforeinstallprompt event fires early — before module scripts load.
// The <head> inline script captures it into window.__installPrompt immediately
// and re-dispatches "installpromptready" so we pick it up here regardless of
// which fires first.
let deferredInstallPrompt = window.__installPrompt || null;

window.addEventListener("installpromptready", () => {
  deferredInstallPrompt = window.__installPrompt;
  syncHelpFab();
});

window.addEventListener("appinstalled", () => {
  deferredInstallPrompt = null;
  window.__installPrompt = null;
  syncHelpFab();
});

function syncHelpFab() {
  const overlayOpen = [...document.querySelectorAll(".panel-backdrop")].some((b) => !b.hidden);
  if (elements.helpFab) elements.helpFab.hidden = overlayOpen;
  // The "Ask" pill follows the same rule, and only appears once the assistant Worker
  // URL is configured (ASSISTANT_API); until then the feature is dormant.
  if (elements.assistantFab) elements.assistantFab.hidden = overlayOpen || !ASSISTANT_API;
  // The install FAB appears only when the browser has deferred an install prompt
  // (Android Chrome); hidden on iOS (no API) and when already installed.
  if (elements.installFab) elements.installFab.hidden = overlayOpen || !deferredInstallPrompt;
  syncTabbar();
}

// topic: "nav" (default, how to move around) or "card" (explain the open person
// panel — opened from the panel's own "?" and layered over it, so we do NOT close
// the detail panel here).
function openGuide(topic = "nav") {
  if (!elements.guidePanel) return;
  guideTopic = ["card", "portrait", "updates", "story"].includes(topic) ? topic : "nav";
  // The guide layers above every panel (z30), so it does NOT close the panel it is
  // explaining — "About what's new"/"About this story" sit over their own panel.
  const opening = elements.guidePanel.hidden;
  if (opening && !elements.guidePanel.contains(document.activeElement)) {
    lastFocused = document.activeElement;
  }
  renderGuide();
  elements.guidePanel.hidden = false;
  elements.guideBackdrop.hidden = false;
  if (opening) {
    elements.guideContent.scrollTop = 0;
    elements.closeGuide.focus();
  }
  syncHelpFab();
  try { localStorage.setItem(GUIDE_STORAGE_KEY, "1"); } catch { /* storage unavailable */ }
}

function closeGuide() {
  if (!elements.guidePanel) return;
  elements.guidePanel.hidden = true;
  elements.guideBackdrop.hidden = true;
  syncHelpFab();
  if (lastFocused && lastFocused.isConnected && typeof lastFocused.focus === "function") {
    lastFocused.focus();
  }
  lastFocused = null;
}

// The "What's new / Novidades" panel — a curated, family-facing feed of recent additions,
// stored as ./updates.yaml (bilingual one-liners + entity links). Mirrors the Family Story
// panel; the engineering CHANGELOG.md is deliberately NOT surfaced here.
let updatesDoc = null;
// When a person is opened from the What's new feed, remember to return to it when that
// person panel is closed (the panel and the feed share the right edge, so the feed is
// closed first). A document opens in the reader overlay on top, so it needs no flag —
// closing the reader simply reveals the feed underneath.
let returnToUpdates = false;
async function loadUpdates() {
  if (!updatesDoc) {
    // Prefer the generated, comprehensive updates.json (every public document + the curated
    // editorial entries); fall back to the curated updates.yaml if the build has not run.
    let doc = null;
    try {
      const jsonResp = await fetch("./updates.json", { cache: "no-store" });
      if (jsonResp.ok) doc = await jsonResp.json();
    } catch { /* fall back to YAML */ }
    if (!doc) {
      const yamlResp = await fetch("./updates.yaml", { cache: "no-store" });
      if (!yamlResp.ok) throw new Error(String(yamlResp.status));
      doc = parseYaml(await yamlResp.text());
    }
    updatesDoc = doc || {};
  }
  const list = Array.isArray(updatesDoc.updates) ? updatesDoc.updates.slice() : [];
  return list.sort((a, b) => String(b.date || "").localeCompare(String(a.date || "")));
}

function monthLabel(iso) {
  const parts = String(iso).split("-").map(Number);
  if (parts.length < 2 || parts.slice(0, 2).some(Number.isNaN)) return "";
  try {
    return new Intl.DateTimeFormat(state.locale === "pt-BR" ? "pt-BR" : "en-GB", {
      year: "numeric", month: "long", timeZone: "UTC",
    }).format(new Date(Date.UTC(parts[0], parts[1] - 1, 1)));
  } catch {
    return "";
  }
}

function formatUpdateDate(iso) {
  if (typeof iso !== "string") return "";
  const parts = iso.split("-").map(Number);
  if (parts.length < 3 || parts.some(Number.isNaN)) return iso;
  try {
    return new Intl.DateTimeFormat(state.locale === "pt-BR" ? "pt-BR" : "en-GB", {
      year: "numeric", month: "long", day: "numeric", timeZone: "UTC",
    }).format(new Date(Date.UTC(parts[0], parts[1] - 1, parts[2])));
  } catch {
    return iso;
  }
}

const UPDATE_SOURCE_RE = /^(CIV|GOV|PAR|PRB|NWS|PUB|REC)-\d+$/;

// Resolve an update link id to { label, open } or null when it cannot be routed
// (a family/event id, or an entity absent under the privacy filter). P-#### opens the
// person panel; a source id opens the record reader.
function resolveUpdateLink(id) {
  if (/^P-\d+$/.test(id)) {
    const person = state.data && state.data.people && state.data.people[id];
    if (!person) return null;
    return {
      label: person.name || id,
      open: () => { returnToUpdates = true; closeUpdates(); openDetails(id); },
    };
  }
  if (UPDATE_SOURCE_RE.test(id)) {
    const source = state.data && state.data.sources && state.data.sources[id];
    if (!source) return null;
    // Open the record reader on top of the feed (z-index 1000); closing it reveals the feed.
    return { label: localeText(source.title, source.titlePt) || id, open: () => openReader(source) };
  }
  return null;
}

// The curated entries this device has seen. The first time, everything already published
// counts as seen, so a new visitor is not greeted by a badge of 40.
function seenUpdateKeys(entries) {
  let seen = null;
  try { seen = JSON.parse(localStorage.getItem(UPDATES_SEEN_KEY) || "null"); } catch { /* unreadable */ }
  if (Array.isArray(seen)) return new Set(seen);
  markUpdatesSeen(entries);
  return new Set(entries.filter(isCurated).map(updateKey));
}

function markUpdatesSeen(entries) {
  try { localStorage.setItem(UPDATES_SEEN_KEY, JSON.stringify(entries.filter(isCurated).map(updateKey))); } catch { /* storage unavailable */ }
}

const updateInScope = (entry) => !state.branches || entryInScope(entry, state.branches, state.scope, state.data?.sources);

// The unread count on the What's new tab and button (and the installed app's icon, where the
// platform supports it): curated entries not yet seen, within the chosen families.
async function refreshUpdatesBadge() {
  if (!state.data) return;
  let entries;
  try { entries = await loadUpdates(); } catch { return; }
  const seen = seenUpdateKeys(entries);
  const count = entries.filter((entry) => isCurated(entry) && !seen.has(updateKey(entry)) && updateInScope(entry)).length;
  for (const badge of document.querySelectorAll("[data-updates-badge]")) {
    badge.hidden = !count;
    badge.textContent = count > 9 ? "9+" : String(count);
  }
  try {
    if (count && navigator.setAppBadge) await navigator.setAppBadge(count);
    else if (!count && navigator.clearAppBadge) await navigator.clearAppBadge();
  } catch { /* badging unsupported or not permitted */ }
}

// The "These families · N / Everything · M" switch shown over a scoped list.
function scopeSwitch(scopedCount, allCount, showingAll, allLabelKey, onChange) {
  const switcher = document.createElement("div");
  switcher.className = "segmented";
  switcher.setAttribute("role", "group");
  for (const [all, label] of [[false, t("search.scope", { n: scopedCount })], [true, t(allLabelKey, { n: allCount })]]) {
    const option = document.createElement("button");
    option.type = "button";
    option.textContent = label;
    option.setAttribute("aria-pressed", String(all === showingAll));
    option.addEventListener("click", () => onChange(all));
    switcher.append(option);
  }
  return switcher;
}

// unseen: keys of curated entries this device had not seen when the panel opened.
function renderUpdates(container, entries, unseen = new Set()) {
  container.textContent = "";
  if (state.scope.size) {
    const scoped = entries.filter(updateInScope);
    container.append(scopeSwitch(scoped.length, entries.length, state.updatesAll, "updates.all", (all) => {
      state.updatesAll = all;
      renderUpdates(container, entries, unseen);
    }));
    if (!state.updatesAll) entries = scoped;
  }
  if (!entries.length) {
    const empty = document.createElement("p");
    empty.className = "empty-note";
    empty.textContent = t("updates.empty");
    container.appendChild(empty);
    return;
  }
  let currentMonth = null;
  for (const entry of entries) {
    const month = String(entry.date || "").slice(0, 7);
    if (month && month !== currentMonth) {
      currentMonth = month;
      const heading = document.createElement("h3");
      heading.className = "update-month";
      heading.textContent = monthLabel(entry.date);
      container.appendChild(heading);
    }

    const item = document.createElement("article");
    item.className = "update-item";

    const meta = document.createElement("div");
    meta.className = "update-meta";
    const kind = document.createElement("span");
    const kindName = entry.kind || "document";
    kind.className = `update-kind update-kind--${kindName}`;
    kind.textContent = t(`updates.kind.${kindName}`);
    const date = document.createElement("time");
    date.className = "update-date";
    if (typeof entry.date === "string") date.dateTime = entry.date;
    date.textContent = formatUpdateDate(entry.date);
    if (unseen.has(updateKey(entry))) {
      const fresh = document.createElement("span");
      fresh.className = "update-new";
      fresh.textContent = t("updates.new");
      meta.append(fresh);
    }
    meta.append(kind, date);
    const tags = state.branches ? branchTagsFor(
      state.branches.list.map((branch) => branch.key).filter((key) => entryBranches(entry, state.branches, state.data?.sources).has(key)),
    ) : null;
    if (tags) meta.append(tags);

    // Headline. When a `primary` entity resolves, the headline itself opens it (the document
    // reader or the person panel); otherwise it is plain text.
    const titleText = localeText(entry.title, entry.title_pt) || "";
    const primary = entry.primary ? resolveUpdateLink(entry.primary) : null;
    let title;
    if (primary) {
      title = document.createElement("button");
      title.type = "button";
      title.className = "update-title update-title-link";
      title.addEventListener("click", primary.open);
    } else {
      title = document.createElement("p");
      title.className = "update-title";
    }
    title.textContent = titleText;

    item.append(meta, title);

    const chips = (Array.isArray(entry.links) ? entry.links : [])
      .filter((id) => id !== entry.primary)
      .map(resolveUpdateLink)
      .filter(Boolean);
    if (chips.length) {
      const links = document.createElement("div");
      links.className = "update-links";
      for (const chip of chips) {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "update-chip";
        btn.textContent = chip.label;
        btn.addEventListener("click", chip.open);
        links.appendChild(btn);
      }
      item.appendChild(links);
    }
    container.appendChild(item);
  }
}

// ---------- "What's new" notifications ----------
// One opt-in bar at the top of the What's new panel. iPhone/iPad only allow web push for a
// site added to the Home Screen and opened from there (iOS 16.4+), and only after a tap,
// so the bar explains that instead of offering a button that cannot work.
let notifyConfigPromise = null;
let notifyRenderToken = 0;
const NOTIFY_SYNC_KEY = "armond-notify-synced";

function pushEnvironment() {
  const ua = navigator.userAgent || "";
  const isIos = /iphone|ipad|ipod/i.test(ua) || (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
  const standalone = window.matchMedia("(display-mode: standalone)").matches || navigator.standalone === true;
  const supported = "serviceWorker" in navigator && "PushManager" in window && "Notification" in window;
  if (isIos && !standalone) return "ios-install";
  return supported ? "supported" : "unsupported";
}

function notifyConfig() {
  if (!NOTIFY_API) return Promise.resolve(null);
  notifyConfigPromise ||= (async () => {
    try {
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), 4000);
      const response = await fetch(`${NOTIFY_API}/health`, { cache: "no-store", signal: controller.signal });
      clearTimeout(timer);
      const data = response.ok ? await response.json() : null;
      if (data && data.ok && data.publicKey) return data;
    } catch { /* offline or slow — try again next time */ }
    notifyConfigPromise = null; // only a successful answer is kept for the session
    return null;
  })();
  return notifyConfigPromise;
}

// `ready` never settles if the service worker failed to register; never wait on it forever.
function serviceWorkerReady() {
  return Promise.race([
    navigator.serviceWorker.ready,
    new Promise((resolve) => setTimeout(() => resolve(null), 4000)),
  ]);
}

async function currentPushSubscription() {
  if (pushEnvironment() !== "supported") return null;
  const registration = await serviceWorkerReady();
  return registration ? registration.pushManager.getSubscription() : null;
}

async function postSubscription(subscription) {
  const response = await fetch(`${NOTIFY_API}/subscribe`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ subscription: subscription.toJSON(), lang: state.locale }),
  });
  if (!response.ok) throw new Error(String(response.status));
  try { localStorage.setItem(NOTIFY_SYNC_KEY, new Date().toISOString().slice(0, 10)); } catch { /* storage unavailable */ }
}

// Re-send this device's subscription at most once a day (an idempotent save), so a device the
// Worker has dropped or lost — or one the browser replaced — quietly recovers.
async function resyncSubscription(subscription) {
  let last = "";
  try { last = localStorage.getItem(NOTIFY_SYNC_KEY) || ""; } catch { /* storage unavailable */ }
  if (last === new Date().toISOString().slice(0, 10)) return;
  try { await postSubscription(subscription); } catch { /* try again on another day */ }
}

async function enableNotifications() {
  const config = await notifyConfig();
  if (!config) throw new Error("notifications unavailable");
  const permission = await Notification.requestPermission();
  if (permission !== "granted") return;
  const registration = await serviceWorkerReady();
  if (!registration) throw new Error("service worker unavailable");
  const subscription = (await registration.pushManager.getSubscription())
    || (await registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: b64urlToBytes(config.publicKey),
    }));
  await postSubscription(subscription);
}

async function disableNotifications() {
  const subscription = await currentPushSubscription();
  if (!subscription) return;
  try {
    await fetch(`${NOTIFY_API}/unsubscribe`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ endpoint: subscription.endpoint }),
    });
  } finally {
    await subscription.unsubscribe();
  }
}

// Re-register with the new language so the next notification arrives in it.
async function refreshPushLanguage() {
  try {
    if (!(await notifyConfig())) return;
    const subscription = await currentPushSubscription();
    if (subscription) await postSubscription(subscription);
  } catch { /* best effort — the old language stays until the next change */ }
}

function b64urlToBytes(text) {
  const base64 = text.replace(/-/g, "+").replace(/_/g, "/");
  const binary = atob(base64 + "=".repeat((4 - (base64.length % 4)) % 4));
  return Uint8Array.from(binary, (char) => char.charCodeAt(0));
}

async function renderNotifyBar(message) {
  const bar = elements.updatesNotify;
  if (!bar) return;
  // Opening the panel, switching language and a notification tap can all render at once;
  // only the newest render may touch the bar, and it swaps its content in one step.
  const token = ++notifyRenderToken;
  const environment = pushEnvironment();
  const config = environment === "unsupported" ? null : await notifyConfig();
  const subscription = config && environment === "supported" && Notification.permission !== "denied"
    ? await currentPushSubscription().catch(() => null)
    : null;
  if (token !== notifyRenderToken) return;
  if (!config) { bar.hidden = true; return; }
  const text = document.createElement("p");
  text.className = "updates-notify-text";
  const content = [text];
  bar.hidden = false;

  if (environment === "ios-install") { text.textContent = t("notify.iosInstall"); bar.replaceChildren(...content); return; }
  if (Notification.permission === "denied") { text.textContent = t("notify.denied"); bar.replaceChildren(...content); return; }

  const subscribed = Boolean(subscription);
  if (subscription) resyncSubscription(subscription);
  const button = document.createElement("button");
  button.type = "button";
  button.className = "update-chip updates-notify-button";
  text.textContent = message || (subscribed ? t("notify.enabled") : t("notify.prompt"));
  button.textContent = subscribed ? t("notify.disable") : t("notify.enable");
  button.addEventListener("click", async () => {
    button.disabled = true;
    button.textContent = t("notify.working");
    try {
      if (subscribed) await disableNotifications();
      else await enableNotifications();
      renderNotifyBar();
    } catch {
      renderNotifyBar(t("notify.error"));
    }
  });
  content.push(button);
  bar.replaceChildren(...content);
}

let openUpdatesUnseen = null;
async function openUpdates() {
  if (!elements.updatesPanel) return;
  closeStory();
  closeDetails();
  const opening = elements.updatesPanel.hidden;
  elements.updatesPanel.hidden = false;
  elements.updatesBackdrop.hidden = false;
  if (opening && !elements.updatesPanel.contains(document.activeElement)) {
    lastFocused = document.activeElement;
  }
  elements.updatesContent.textContent = t("updates.loading");
  renderNotifyBar();
  if (opening) elements.closeUpdates.focus();
  try {
    const entries = await loadUpdates();
    // NEW marks what was unread when the panel opened; opening it then marks everything read.
    if (opening || !openUpdatesUnseen) {
      const seen = seenUpdateKeys(entries);
      openUpdatesUnseen = new Set(entries.filter((entry) => isCurated(entry) && !seen.has(updateKey(entry))).map(updateKey));
    }
    renderUpdates(elements.updatesContent, entries, openUpdatesUnseen);
    if (opening) elements.updatesContent.scrollTop = 0;
    markUpdatesSeen(entries);
    refreshUpdatesBadge();
  } catch {
    elements.updatesContent.textContent = t("updates.error");
  }
}

function closeUpdates() {
  if (!elements.updatesPanel || elements.updatesPanel.hidden) return;
  openUpdatesUnseen = null;
  elements.updatesPanel.hidden = true;
  elements.updatesBackdrop.hidden = true;
  if (lastFocused && lastFocused.isConnected && typeof lastFocused.focus === "function") {
    lastFocused.focus();
  }
  lastFocused = null;
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
  if (returnToUpdates) { returnToUpdates = false; openUpdates(); }
  if (returnToAssistant) { returnToAssistant = false; openAssistant(); }
}

// ---------- Mobile focus view ----------
// A phone-native alternative to the horizontal pedigree: one person centred at a
// time, with tappable rows for parents, partners, children and siblings. It reuses
// the same projected data and presentation helpers as the desktop tree; only the
// layout differs, chosen at runtime by viewport width.

const MOBILE_QUERY = window.matchMedia("(max-width: 700px)");
const isMobile = () => MOBILE_QUERY.matches;

// One tappable relation row. Rows for a modelled person we can re-centre on are
// buttons; documented-only relations (no entity) are inert. options.tags adds the person's
// branch tags; options.colour draws that branch's colour down the row's edge.
function mobileRelationRow(id, name, meta, options = {}) {
  const target = id && state.data.people[id];
  const row = document.createElement(target ? "button" : "div");
  row.className = `mobile-row${target ? "" : " is-static"}${options.colour ? " has-branch-edge" : ""}`;
  if (options.colour) row.style.setProperty("--b", options.colour);
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
  const tags = options.tags && target ? branchTags(id) : null;
  if (tags) row.append(tags);
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

// Back to the home screen of the chosen families.
function showHome() {
  if (elements.detailsPanel && !elements.detailsPanel.hidden) closeDetails();
  state.focusId = null;
  state.focusHistory = [];
  state.homeView = null;
  if (isMobile()) {
    renderMobileFocus();
    scrollFocusIntoView();
  }
}

function showHomeView(view) {
  state.homeView = view;
  renderMobileFocus();
  scrollFocusIntoView();
}

function mobileNavButton(label, onClick, extraClass = "") {
  const button = document.createElement("button");
  button.type = "button";
  button.className = `mobile-nav-btn ${extraClass}`.trim();
  button.textContent = label;
  button.addEventListener("click", onClick);
  return button;
}

// A titled block holding any content (mobileSection holds rows).
function mobileBlock(title, content) {
  const section = document.createElement("section");
  section.className = "mobile-section";
  const heading = document.createElement("h3");
  heading.className = "mobile-section-title";
  heading.textContent = title;
  section.append(heading, content);
  return section;
}

const scopedPeopleIds = () => Object.keys(state.data.people).filter(personInScope);

function surnameChip(entry, onClick) {
  const chip = document.createElement("button");
  chip.type = "button";
  chip.className = "surname-chip";
  chip.textContent = entry.label;
  const count = document.createElement("span");
  count.className = "surname-chip-count";
  count.textContent = String(entry.ids.length);
  chip.append(count);
  chip.addEventListener("click", onClick);
  return chip;
}

// The home screen: the four grandparents (everything), or where the chosen families meet and
// those grandparents' parents; then a surname index. Living people never lead a scoped home.
function renderMobileHome(container) {
  const people = state.data.people;
  const chosen = chosenBranches().filter((branch) => people[branch.rootId]);
  const scoped = state.scope.size > 0;

  const roots = document.createElement("div");
  roots.className = "mobile-list home-roots";
  for (const branch of chosen) {
    roots.append(mobileRelationRow(branch.rootId, people[branch.rootId].name, null, { tags: true, colour: branch.colour }));
  }
  if (scoped && chosen.length === 2) {
    const spouse = (people[chosen[0].rootId].spouses || []).find((entry) => entry.id === chosen[1].rootId);
    if (spouse?.marriage?.date) {
      const married = document.createElement("p");
      married.className = "home-married";
      married.textContent = `${t("home.married")}${bioWhen(spouse.marriage.date)}`;
      roots.append(married);
    }
  }
  const title = !scoped ? t("home.fourRivers") : chosen.length === 1 ? t("home.single") : t("home.meet");
  container.append(mobileBlock(title, roots));

  if (scoped) {
    const parentIds = [...new Set(chosen.flatMap((branch) =>
      (state.data.parentsByChild[branch.rootId] || []).filter(relationshipVisible).map((entry) => entry.parentId)))];
    const rows = parentIds.map((id) => mobileRelationRow(id, people[id]?.name || id, null, { tags: true }));
    container.append(mobileSection(chosen.length === 1 ? t("detail.parents") : t("home.parents"), rows, t("empty.parents")));
  }

  const browse = document.createElement("button");
  browse.type = "button";
  browse.className = "home-browse";
  browse.textContent = t("home.browseTree");
  browse.addEventListener("click", () => focusPerson(scoped ? chosen[0].rootId : SUBJECT_ID));
  container.append(browse);

  const index = surnameIndex(people, scopedPeopleIds(), state.branches.vocabulary);
  if (index.length) {
    const chips = document.createElement("div");
    chips.className = "surname-chips";
    for (const entry of index.slice(0, 8)) chips.append(surnameChip(entry, () => showHomeView(`surname:${entry.key}`)));
    const all = document.createElement("button");
    all.type = "button";
    all.className = "surname-chip surname-chip-all";
    all.textContent = `${t("home.allSurnames")} ›`;
    all.addEventListener("click", () => showHomeView("surnames"));
    chips.append(all);
    container.append(mobileBlock(t("home.surnames"), chips));
  }
}

// Every surname in the chosen families, A–Z, or the people who carry one.
function renderSurnameView(container) {
  const people = state.data.people;
  const index = surnameIndex(people, scopedPeopleIds(), state.branches.vocabulary);
  const nav = document.createElement("div");
  nav.className = "mobile-nav";
  const key = state.homeView.startsWith("surname:") ? state.homeView.slice(8) : null;
  nav.append(mobileNavButton(`‹ ${t("mobile.back")}`, () => showHomeView(key ? "surnames" : null)));
  nav.append(mobileNavButton(`⌂ ${t("mobile.home")}`, showHome, "mobile-nav-home"));
  container.append(nav);

  if (key) {
    const entry = index.find((item) => item.key === key);
    const rows = (entry?.ids || []).map((id) => mobileRelationRow(id, people[id].name, null, { tags: !state.scope.size || state.scope.size > 1 }));
    container.append(mobileSection(entry ? entry.spellings.join(" · ") : key, rows, t("home.none")));
    return;
  }
  const byLetter = new Map();
  for (const entry of [...index].sort((a, b) => a.label.localeCompare(b.label))) {
    const letter = entry.label[0].normalize("NFD")[0].toUpperCase();
    if (!byLetter.has(letter)) byLetter.set(letter, []);
    byLetter.get(letter).push(entry);
  }
  const title = document.createElement("h2");
  title.className = "mobile-screen-title";
  title.textContent = t("home.surnameTitle", { families: scopeLabel() });
  container.append(title);
  for (const [letter, entries] of byLetter) {
    const chips = document.createElement("div");
    chips.className = "surname-chips";
    for (const entry of entries) chips.append(surnameChip(entry, () => showHomeView(`surname:${entry.key}`)));
    container.append(mobileBlock(letter, chips));
  }
}

function renderMobileFocus() {
  const container = elements.mobileView;
  if (!container || !state.data) return;
  container.replaceChildren();
  if (!state.focusId && state.branches) {
    if (state.homeView) renderSurnameView(container);
    else renderMobileHome(container);
    return;
  }
  const person = state.data.people[state.focusId] || state.data.people[state.rootId];
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
  nav.append(mobileNavButton(`⌂ ${t("mobile.home")}`, showHome, "mobile-nav-home"));
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
  const tags = branchTags(person.id);
  if (tags) {
    const line = document.createElement("p");
    line.className = "mobile-focus-tags";
    line.append(tags);
    head.append(line);
  }
  const relTerm = relationshipTerm(person);
  if (relTerm && person.id !== SUBJECT_ID) {
    const chip = document.createElement("p");
    chip.className = "mobile-focus-rel";
    chip.textContent = `${t("detail.relationship", { name: subjectLabel() })}: ${relTerm}`;
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
  container.append(mobileSection(`${t("detail.parents")} ↑`, parentRows, t("empty.parents")));

  const spouseRows = (person.spouses || []).map((spouse) =>
    mobileRelationRow(spouse.id, spouse.name, spouse.marriage?.date ? bioWhen(spouse.marriage.date) : null),
  );
  container.append(mobileSection(t("detail.marriages"), spouseRows, t("empty.partners")));

  const childRows = (person.children || []).map((child) => mobileRelationRow(child.id, child.name));
  container.append(mobileSection(`${t("detail.children")} ↓`, childRows, t("empty.children")));

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

// ---------- Choosing families ----------
// One panel, two modes. "welcome" is the first-visit question — Everything first and already
// chosen, so for the main user it is a single tap — with a card per branch. "switch" is the
// sheet behind the header chip: live toggles, back to Everything, and a link to share.
let branchPanelMode = "switch";
let branchDraft = new Set();
let afterBranchWelcome = null;

function renderBranchChips() {
  if (!state.branches) return;
  const keys = chosenBranches().map((branch) => branch.key);
  for (const chip of [elements.branchChip, elements.branchChipToolbar]) {
    if (!chip) continue;
    const label = document.createElement("span");
    label.className = "branch-chip-label";
    label.textContent = scopeLabel();
    const caret = document.createElement("span");
    caret.className = "branch-chip-caret";
    caret.setAttribute("aria-hidden", "true");
    caret.textContent = "▾";
    chip.replaceChildren(branchDots(keys), label, caret);
    chip.setAttribute("aria-label", t("branch.chipAria", { families: scopeLabel() }));
    chip.hidden = false;
  }
}

// Apply a choice everywhere: the tree's starting person, the home screen, search, What's new,
// the story and the address (so the view can be shared).
function applyScope(scope, { persist = true } = {}) {
  state.scope = normaliseScope(scope, state.branches);
  if (persist) {
    try { localStorage.setItem(BRANCH_STORAGE_KEY, serialiseScope(state.scope, state.branches)); } catch { /* storage unavailable */ }
  }
  state.searchAll = false;
  state.updatesAll = false;
  state.storyFullOrder = false;
  state.rootId = scopeRoot(state.branches, state.scope);
  state.focusId = null;
  state.focusHistory = [];
  state.homeView = null;
  state.toggled.clear();
  state.autoFit = true;
  if (elements.rootSelect) elements.rootSelect.value = state.rootId;
  renderBranchChips();
  updateSearchPlaceholder();
  hideSearchResults();
  renderActive();
  refreshUpdatesBadge();
  if (elements.updatesPanel && !elements.updatesPanel.hidden) openUpdates();
  if (elements.storyPanel && !elements.storyPanel.hidden) openStory();
  syncHash();
}

function shareUrl() {
  const params = new URLSearchParams();
  if (state.scope.size) params.set("branch", serialiseScope(state.scope, state.branches));
  params.set("lang", state.locale);
  return `${location.origin}${location.pathname}#${params.toString().replace(/%2C/g, ",")}`;
}

function setBranchDraft(next, focusKey) {
  branchDraft = normaliseScope(next, state.branches);
  if (branchPanelMode === "switch") applyScope(branchDraft);
  renderBranchPanel();
  const again = elements.branchContent.querySelector(`[data-branch-key="${focusKey}"]`);
  if (again) again.focus();
}

function toggleBranchDraft(key) {
  if (key === "all") return setBranchDraft(new Set(), "all");
  const next = new Set(branchDraft);
  if (next.has(key)) next.delete(key); else next.add(key);
  setBranchDraft(next, key);
}

// A branch as a card (welcome) or a switch row (sheet). key "all" is Everything.
function branchOption(key, title, subtitle, colourKeys, pressed) {
  const welcome = branchPanelMode === "welcome";
  const button = document.createElement("button");
  button.type = "button";
  button.className = welcome ? `branch-card${key === "all" ? " is-everything" : ""}` : "branch-row";
  button.dataset.branchKey = key;
  button.setAttribute("aria-pressed", String(pressed));
  const colour = key === "all" ? "var(--green)" : state.branches.byKey[key].colour;
  button.style.setProperty("--b", colour);
  if (welcome) {
    const stripe = document.createElement("span");
    stripe.className = "branch-card-stripe";
    if (key === "all") {
      stripe.style.background = `linear-gradient(${state.branches.list.map((branch, i, all) =>
        `${branch.colour} ${(i / all.length) * 100}% ${((i + 1) / all.length) * 100}%`).join(", ")})`;
    }
    button.append(stripe);
  } else {
    button.append(branchDots(colourKeys));
  }
  const body = document.createElement("span");
  body.className = "branch-option-body";
  const heading = document.createElement("span");
  heading.className = "branch-option-title";
  heading.textContent = title;
  const sub = document.createElement("span");
  sub.className = "branch-option-sub";
  sub.textContent = subtitle;
  body.append(heading, sub);
  const branch = state.branches.byKey[key];
  if (welcome && branch?.surnames.length) {
    const surnames = document.createElement("span");
    surnames.className = "branch-option-surnames";
    surnames.textContent = branch.surnames.join(" · ");
    body.append(surnames);
  }
  if (welcome && key === "all") body.append(branchDots(colourKeys));
  const mark = document.createElement("span");
  mark.className = welcome ? "branch-check" : "branch-switch";
  mark.setAttribute("aria-hidden", "true");
  button.append(body, mark);
  button.addEventListener("click", () => toggleBranchDraft(key));
  return button;
}

function renderBranchPanel() {
  const panel = elements.branchContent;
  if (!panel || !state.branches) return;
  const welcome = branchPanelMode === "welcome";
  const total = Object.keys(state.data.people).length;
  const allKeys = state.branches.list.map((branch) => branch.key);
  panel.replaceChildren();

  const head = document.createElement("div");
  head.className = "branch-head";
  const title = document.createElement("h2");
  title.id = "branch-title";
  title.className = "story-title";
  title.textContent = welcome ? t("branch.welcomeTitle") : t("branch.sheetTitle");
  const lede = document.createElement("p");
  lede.className = "branch-lede";
  lede.textContent = welcome ? t("branch.welcomeLede") : t("branch.sheetLede");
  head.append(title, lede);
  panel.append(head);

  panel.append(branchOption("all", t("branch.everything"), t("branch.everythingSub", { n: total }), allKeys, branchDraft.size === 0));
  if (welcome) {
    const or = document.createElement("p");
    or.className = "branch-or";
    or.textContent = t("branch.or");
    panel.append(or);
  }
  for (const side of ["paternal", "maternal", null]) {
    const group = state.branches.list.filter((branch) => branch.side === side);
    if (!group.length) continue;
    const sideHead = document.createElement("div");
    sideHead.className = "branch-side-head";
    const label = document.createElement("h3");
    label.textContent = side ? t("branch.side", { label: group[0].label }) : t("branch.otherSide");
    if (group.length === 2) {
      const couple = document.createElement("span");
      couple.className = "branch-side-couple";
      couple.textContent = t("branch.couple", { a: firstName(group[0].name), b: firstName(group[1].name) });
      label.append(" ", couple);
    }
    sideHead.append(label);
    if (group.length > 1) {
      const both = document.createElement("button");
      both.type = "button";
      both.className = "branch-both";
      both.textContent = t("branch.selectBoth");
      both.addEventListener("click", () => setBranchDraft(new Set(group.map((branch) => branch.key)), group[0].key));
      sideHead.append(both);
    }
    panel.append(sideHead);
    for (const branch of group) {
      const subtitle = welcome
        ? (branch.earliestYear
          ? t("branch.cardSub", { name: branch.name, n: branch.members.length, year: branch.earliestYear })
          : t("branch.cardSubNoYear", { name: branch.name, n: branch.members.length }))
        : t("branch.rowSub", { name: firstName(branch.name), n: branch.members.length });
      panel.append(branchOption(branch.key, branch.label, subtitle, [branch.key], branchDraft.has(branch.key)));
    }
  }

  const footer = document.createElement("div");
  footer.className = "branch-footer";
  if (welcome) {
    const cta = document.createElement("button");
    cta.type = "button";
    cta.className = "branch-cta";
    cta.textContent = branchDraft.size
      ? t("branch.explore", { families: scopeLabel(branchDraft), n: scopeSize(state.branches, branchDraft, total) })
      : t("branch.exploreAll", { n: total });
    cta.addEventListener("click", closeBranchPanel);
    const hint = document.createElement("p");
    hint.className = "branch-hint";
    hint.textContent = t("branch.welcomeHint");
    footer.append(cta, hint);
  } else {
    const share = document.createElement("div");
    share.className = "branch-share";
    const shareTitle = document.createElement("p");
    shareTitle.className = "branch-share-title";
    shareTitle.textContent = t("branch.share");
    const url = document.createElement("code");
    url.textContent = shareUrl();
    const actions = document.createElement("div");
    actions.className = "branch-share-actions";
    const copy = document.createElement("button");
    copy.type = "button";
    copy.className = "update-chip";
    copy.textContent = t("branch.copy");
    copy.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(shareUrl());
        copy.textContent = t("branch.copied");
      } catch {
        copy.textContent = t("branch.copyFailed");
      }
    });
    actions.append(copy);
    if (navigator.share) {
      const send = document.createElement("button");
      send.type = "button";
      send.className = "update-chip";
      send.textContent = t("branch.send");
      send.addEventListener("click", () => {
        navigator.share({ title: t("page.title"), url: shareUrl() }).catch(() => { /* dismissed */ });
      });
      actions.append(send);
    }
    share.append(shareTitle, url, actions);
    const done = document.createElement("button");
    done.type = "button";
    done.className = "branch-cta";
    done.textContent = t("branch.done");
    done.addEventListener("click", closeBranchPanel);
    footer.append(share, done);
  }
  panel.append(footer);
}

function openBranchPanel(mode = "switch") {
  if (!state.branches || !elements.branchPanel) return;
  closeAppMenu();
  branchPanelMode = mode;
  branchDraft = new Set(state.scope);
  if (!elements.branchPanel.contains(document.activeElement)) lastFocused = document.activeElement;
  elements.branchPanel.classList.toggle("is-welcome", mode === "welcome");
  renderBranchPanel();
  elements.branchPanel.hidden = false;
  elements.branchBackdrop.hidden = false;
  elements.branchPanel.scrollTop = 0;
  elements.branchContent.querySelector("[aria-pressed='true']")?.focus();
}

// Closing the welcome question applies its choice (Everything unless changed).
function closeBranchPanel() {
  if (!elements.branchPanel || elements.branchPanel.hidden) return;
  const welcome = branchPanelMode === "welcome";
  if (welcome) applyScope(branchDraft);
  elements.branchPanel.hidden = true;
  elements.branchBackdrop.hidden = true;
  if (lastFocused && lastFocused.isConnected && typeof lastFocused.focus === "function") lastFocused.focus();
  lastFocused = null;
  if (welcome && afterBranchWelcome) {
    const next = afterBranchWelcome;
    afterBranchWelcome = null;
    next();
  }
}

// ---------- Bottom tab bar (mobile) ----------
// Family · What's new · Story · Ask AI, always one thumb-tap away. The panels it opens are
// the same ones the desktop buttons open; on a phone they fill the screen above the bar.
function activeTab() {
  if (elements.assistantPanel && !elements.assistantPanel.hidden) return "assistant";
  if (elements.updatesPanel && !elements.updatesPanel.hidden) return "updates";
  if (elements.storyPanel && !elements.storyPanel.hidden) return "story";
  return "family";
}

function syncTabbar() {
  const active = activeTab();
  for (const tab of elements.tabs) {
    const on = tab.dataset.tab === active;
    tab.classList.toggle("is-active", on);
    if (on) tab.setAttribute("aria-current", "page");
    else tab.removeAttribute("aria-current");
  }
}

function openTab(name) {
  const wasHome = activeTab() === "family" && elements.detailsPanel.hidden;
  hideSearchResults();
  // Switching tabs is not "going back": drop the return-to-panel flags before closing.
  returnToUpdates = false;
  returnToAssistant = false;
  if (!elements.detailsPanel.hidden) closeDetails();
  if (name !== "assistant") closeAssistant();
  if (name !== "story") closeStory();
  if (name !== "updates") closeUpdates();
  if (name === "updates") openUpdates();
  else if (name === "story") openStory();
  else if (name === "assistant") openAssistant();
  else if (wasHome) showHome(); // tapping Family again goes home
  syncTabbar();
}

// ---------- Emblem menu ----------
// The emblem opens a small menu: families, help, language and "Add to Home Screen" — the
// rarely used controls that floated over the page before the tab bar.
function closeAppMenu() {
  if (!elements.appMenu || elements.appMenu.hidden) return;
  elements.appMenu.hidden = true;
  elements.appMenuButton?.setAttribute("aria-expanded", "false");
}

function renderAppMenu() {
  const menu = elements.appMenu;
  menu.replaceChildren();
  const item = (label, action) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "app-menu-item";
    button.setAttribute("role", "menuitem");
    button.textContent = label;
    button.addEventListener("click", () => { closeAppMenu(); action(); });
    menu.append(button);
  };
  if (state.branches) item(t("menu.families"), () => openBranchPanel("switch"));
  item(t("menu.help"), () => openGuide("nav"));
  const languages = document.createElement("div");
  languages.className = "app-menu-languages";
  languages.setAttribute("role", "group");
  languages.setAttribute("aria-label", t("control.language"));
  for (const [code, label] of [["en", "English"], ["pt-BR", "Português"]]) {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = label;
    button.setAttribute("aria-pressed", String(state.locale === code));
    button.addEventListener("click", () => { closeAppMenu(); setLocale(code); });
    languages.append(button);
  }
  menu.append(languages);
  if (deferredInstallPrompt) {
    item(t("install.fab"), async () => {
      if (!deferredInstallPrompt) return;
      await deferredInstallPrompt.prompt();
      deferredInstallPrompt = null;
    });
  }
}

function toggleAppMenu() {
  if (!elements.appMenu) return;
  if (!elements.appMenu.hidden) { closeAppMenu(); return; }
  renderAppMenu();
  elements.appMenu.hidden = false;
  elements.appMenuButton.setAttribute("aria-expanded", "true");
  elements.appMenu.querySelector("button")?.focus();
}

function bindEvents() {
  // A tapped notification focuses this already-open window and asks for the feed.
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.addEventListener("message", (event) => {
      if (event.data && event.data.type === "open-updates") openUpdates();
    });
  }

  // Switch layouts when the viewport crosses the mobile breakpoint (e.g. rotate).
  MOBILE_QUERY.addEventListener("change", () => {
    if (state.data) renderActive();
  });

  elements.rootSelect.addEventListener("change", () => {
    setRoot(elements.rootSelect.value);
  });

  elements.generationLimit.addEventListener("change", () => {
    state.generations = Number(elements.generationLimit.value);
    state.toggled.clear(); // the base depth changed; drop per-card overrides
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
    searchHideTimer = setTimeout(hideSearchResults, 200);
  });

  elements.reset.addEventListener("click", () => {
    state.rootId = scopeRoot(state.branches, state.scope);
    state.focusId = null;
    state.homeView = null;
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

  // Families: the header chip (mobile) and the toolbar chip (desktop) open the same sheet.
  for (const chip of [elements.branchChip, elements.branchChipToolbar]) {
    if (chip) chip.addEventListener("click", () => openBranchPanel("switch"));
  }
  if (elements.branchBackdrop) elements.branchBackdrop.addEventListener("click", closeBranchPanel);
  for (const tab of elements.tabs) tab.addEventListener("click", () => openTab(tab.dataset.tab));
  if (!ASSISTANT_API) elements.tabs.filter((tab) => tab.dataset.tab === "assistant").forEach((tab) => { tab.hidden = true; });
  if (elements.appMenuButton) elements.appMenuButton.addEventListener("click", (event) => { event.stopPropagation(); toggleAppMenu(); });
  document.addEventListener("click", (event) => {
    if (elements.appMenu && !elements.appMenu.hidden && !elements.appMenu.contains(event.target)) closeAppMenu();
  });
  if (elements.detailsBack) elements.detailsBack.addEventListener("click", closeDetails);
  // A tap on the results list must not blur the box (which would close the list first).
  if (elements.searchResults) elements.searchResults.addEventListener("mousedown", (event) => event.preventDefault());

  elements.closeDetails.addEventListener("click", closeDetails);
  elements.backdrop.addEventListener("click", closeDetails);
  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape" || elements.detailsPanel.hidden) return;
    // Let a help/story/updates/families overlay on top of the card take Escape first.
    if (elements.guidePanel && !elements.guidePanel.hidden) return;
    if (elements.branchPanel && !elements.branchPanel.hidden) return;
    if (elements.storyPanel && !elements.storyPanel.hidden) return;
    if (elements.updatesPanel && !elements.updatesPanel.hidden) return;
    closeDetails();
  });

  if (elements.openStory) elements.openStory.addEventListener("click", openStory);
  if (elements.closeStory) elements.closeStory.addEventListener("click", closeStory);
  if (elements.storyBackdrop) elements.storyBackdrop.addEventListener("click", closeStory);
  if (elements.openUpdates) elements.openUpdates.addEventListener("click", openUpdates);
  if (elements.closeUpdates) elements.closeUpdates.addEventListener("click", closeUpdates);
  if (elements.updatesBackdrop) elements.updatesBackdrop.addEventListener("click", closeUpdates);
  if (elements.assistantFab) elements.assistantFab.addEventListener("click", openAssistant);
  if (elements.installFab) {
    elements.installFab.addEventListener("click", async () => {
      if (!deferredInstallPrompt) return;
      elements.installFab.hidden = true;
      await deferredInstallPrompt.prompt();
      deferredInstallPrompt = null;
    });
  }
  if (elements.closeAssistant) elements.closeAssistant.addEventListener("click", closeAssistant);
  if (elements.assistantBackdrop) elements.assistantBackdrop.addEventListener("click", closeAssistant);
  if (elements.assistantForm) {
    elements.assistantForm.addEventListener("submit", (event) => {
      event.preventDefault();
      submitAssistant();
    });
  }
  if (elements.assistantInput) {
    elements.assistantInput.addEventListener("input", autoGrowAssistantInput);
    elements.assistantInput.addEventListener("keydown", (event) => {
      // Enter sends; Shift+Enter inserts a newline.
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        submitAssistant();
      }
    });
  }
  if (elements.helpFab) elements.helpFab.addEventListener("click", () => openGuide("nav"));
  if (elements.detailHelp) elements.detailHelp.addEventListener("click", () => openGuide("card"));
  if (elements.storyHelp) elements.storyHelp.addEventListener("click", () => openGuide("story"));
  if (elements.updatesHelp) elements.updatesHelp.addEventListener("click", () => openGuide("updates"));
  if (elements.detailAskAi) elements.detailAskAi.addEventListener("click", openAssistant);
  if (elements.storyAskAi) elements.storyAskAi.addEventListener("click", openAssistant);
  if (elements.updatesAskAi) elements.updatesAskAi.addEventListener("click", openAssistant);
  if (!ASSISTANT_API) {
    for (const btn of document.querySelectorAll(".panel-ai-btn")) btn.hidden = true;
  }
  if (elements.closeGuide) elements.closeGuide.addEventListener("click", closeGuide);
  if (elements.guideBackdrop) elements.guideBackdrop.addEventListener("click", closeGuide);
  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") return;
    if (elements.appMenu && !elements.appMenu.hidden) { closeAppMenu(); elements.appMenuButton?.focus(); return; }
    // The guide layers on top — Escape closes it first, leaving the panel beneath open.
    if (elements.guidePanel && !elements.guidePanel.hidden) { closeGuide(); return; }
    if (elements.branchPanel && !elements.branchPanel.hidden) { closeBranchPanel(); return; }
    if (elements.assistantPanel && !elements.assistantPanel.hidden) closeAssistant();
    if (elements.storyPanel && !elements.storyPanel.hidden) closeStory();
    if (elements.updatesPanel && !elements.updatesPanel.hidden) closeUpdates();
  });

  // Keep the floating "?" in step with the overlays without patching every
  // open/close path: watch each modal backdrop's `hidden` attribute.
  if (elements.helpFab) {
    const backdropObserver = new MutationObserver(syncHelpFab);
    for (const b of document.querySelectorAll(".panel-backdrop")) {
      backdropObserver.observe(b, { attributes: true, attributeFilter: ["hidden"] });
    }
  }
}

async function initialise() {
  bindEvents();
  // Resolve the display language before anything renders, so the chrome and the
  // loading text appear localised immediately.
  state.locale = resolveInitialLocale(readHash().lang);
  i18n = createI18n(state.locale);
  if (elements.languageSelect) elements.languageSelect.value = state.locale;
  applyStaticTranslations();
  // Independent of the tree data — fetch in parallel; failures stay silent.
  initVisitorWelcome();
  loadAssistantSuggestions();
  try {
    const response = await fetch("/api/tree", { cache: "no-store" });
    if (!response.ok) throw new Error(t("error.httpStatus", { status: response.status }));
    state.data = await response.json();
    state.branches = computeBranches(state.data);

    // The families to show: a shared link's choice (remembered from then on), else this
    // device's earlier choice. Nothing chosen yet means the first-visit question.
    const hash = readHash();
    let storedScope = null;
    try { storedScope = localStorage.getItem(BRANCH_STORAGE_KEY); } catch { /* storage unavailable */ }
    const scopeFromLink = hash.branch !== null;
    state.scope = parseScope(scopeFromLink ? hash.branch : storedScope || "", state.branches);
    if (scopeFromLink) {
      try { localStorage.setItem(BRANCH_STORAGE_KEY, serialiseScope(state.scope, state.branches)); } catch { /* storage unavailable */ }
    }
    const askForFamilies = !scopeFromLink && storedScope === null && !hash.sel;

    // Restore a shared/bookmarked view from the URL hash. A root other than the families'
    // own starting person opens on that person; otherwise the phone shows the home screen.
    const defaultRoot = scopeRoot(state.branches, state.scope);
    state.rootId = hash.root && state.data.people[hash.root] ? hash.root : defaultRoot;
    if (hash.gen && /^[2-6]$/.test(hash.gen)) state.generations = Number(hash.gen);
    state.focusId = state.rootId === defaultRoot ? null : state.rootId;
    renderBranchChips();
    updateSearchPlaceholder();

    populatePersonSelect();
    elements.rootSelect.value = state.rootId;
    elements.generationLimit.value = String(state.generations);
    elements.personCount.textContent = String(Object.keys(state.data.people).length);
    elements.familyCount.textContent = String(state.data.familyCount);
    elements.sourceCount.textContent = String(Object.keys(state.data.sources).length);
    elements.loading.hidden = true;
    renderActive();
    syncHelpFab();
    refreshUpdatesBadge();
    // Re-render the updates panel if it was opened before entity data finished loading
    // (common on slow connections or when the user taps "What's new" immediately on
    // PWA launch — chips resolve only once state.data is populated).
    if (elements.updatesPanel && !elements.updatesPanel.hidden) openUpdates();
    if (hash.sel && state.data.people[hash.sel]) openDetails(hash.sel);
    else syncHash();
    // Opened from a "What's new" notification: show the feed, then drop the flag so a
    // reload or a shared link does not reopen it.
    const search = new URLSearchParams(location.search);
    if (search.get("open") === "updates") {
      openUpdates();
      search.delete("open");
      const query = search.toString();
      history.replaceState(null, "", `${location.pathname}${query ? `?${query}` : ""}${location.hash}`);
    }
    // First visit: open the guide once so a newcomer is oriented before exploring.
    // Skipped when arriving on a deep link (a shared person/record) — they came for
    // that, not the tour — and never again after it has been seen.
    let guideSeen = true;
    try { guideSeen = Boolean(localStorage.getItem(GUIDE_STORAGE_KEY)); } catch { /* storage unavailable */ }
    const showGuide = !guideSeen && !hash.sel;
    // The families question comes first; the guide (if still unseen) follows it.
    if (askForFamilies) {
      if (showGuide) afterBranchWelcome = () => openGuide("nav");
      openBranchPanel("welcome");
    } else if (showGuide) {
      openGuide("nav");
    }
  } catch (error) {
    elements.loading.hidden = true;
    elements.error.hidden = false;
    elements.error.textContent = t("error.loadFailed", { message: error.message });
  }
}

initialise();
