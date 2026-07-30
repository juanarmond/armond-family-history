"use strict";

const state = {
  data: null,
  rootId: "P-0001",
  generations: 4,
  showHypotheses: true,
  visibleNodes: 0,
  zoom: 1,
  autoFit: true,
  selected: null,
};

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
  showHypotheses: document.querySelector("#show-hypotheses"),
  reset: document.querySelector("#reset-view"),
  loading: document.querySelector("#loading"),
  error: document.querySelector("#error"),
  tree: document.querySelector("#tree"),
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
};

const statusLabels = {
  confirmed: "Confirmed",
  "strong-evidence": "Strong evidence",
  hypothesis: "Hypothesis",
  rejected: "Rejected",
  unknown: "Unspecified",
};

const statusColours = {
  confirmed: "var(--confirmed)",
  "strong-evidence": "var(--strong)",
  hypothesis: "var(--hypothesis)",
  rejected: "#8f4d4d",
  unknown: "var(--unknown)",
};

function text(value, fallback = "Unknown") {
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
  if (!event?.date) return "Unknown date";
  const date = event.date;
  if (date.kind === "exact") return date.value;
  if (date.kind === "month") return `${String(date.month).padStart(2, "0")}/${date.year}`;
  if (date.kind === "year") return String(date.year);
  return date.text || "Unknown date";
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
  return person.privacy === "living" ? "Living person" : "Dates not established";
}

function primaryPlace(person) {
  const preferred = person.events.find((event) => event.type === "birth")
    || person.events.find((event) => event.type === "death")
    || person.events[0];
  return preferred?.place?.name || "Place not established";
}

function relationshipVisible(relationship) {
  if (relationship.status === "rejected") return false;
  if (relationship.status === "hypothesis" && !state.showHypotheses) return false;
  return true;
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
  button.setAttribute("aria-label", `Open details for ${person.name}`);

  const avatar = document.createElement("span");
  avatar.className = "avatar";
  avatar.textContent = initials(person.name);

  const main = document.createElement("span");
  const name = document.createElement("strong");
  name.className = "person-name";
  name.textContent = person.name;
  const years = document.createElement("span");
  years.className = "person-years";
  years.textContent = lifespan(person);
  const place = document.createElement("span");
  place.className = "person-place";
  place.textContent = primaryPlace(person);
  main.append(name, years, place);

  const meta = document.createElement("span");
  meta.className = "card-meta";
  if (relationship) meta.append(createBadge(statusLabels[status] || status, status));
  if (person.sourceCount) meta.append(createBadge(`${person.sourceCount} source${person.sourceCount === 1 ? "" : "s"}`));
  if (person.hasConflict) meta.append(createBadge("Conflict", "conflict"));
  if (person.privacy === "living") meta.append(createBadge("Private"));

  button.append(avatar, main, meta);
  button.title = "Click for details · double-click to centre the tree here";
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
  stop.textContent = "Generation limit reached";
  return stop;
}

function createMarriageBadge(marriage) {
  const badge = document.createElement("div");
  badge.className = "marriage-badge";
  const year = yearFromEvent({ date: marriage.date });
  badge.textContent = year ? `⚭ ${year}` : "⚭";
  const detail = [marriage.place, statusLabels[marriage.status] || marriage.status].filter(Boolean);
  badge.title = `Marriage${detail.length ? ` — ${detail.join(" · ")}` : ""}`;
  return badge;
}

function setRoot(personId) {
  if (!state.data.people[personId]) return;
  state.rootId = personId;
  state.autoFit = true;
  if (elements.rootSelect) elements.rootSelect.value = personId;
  renderTree();
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

  const parents = (state.data.parentsByChild[personId] || [])
    .filter(relationshipVisible)
    .sort((a, b) => state.data.people[a.parentId]?.name.localeCompare(state.data.people[b.parentId]?.name || "") || 0);

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
    elements.error.textContent = `Person ${state.rootId} is not available.`;
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

function setZoom(nextZoom) {
  const viewport = elements.treeViewport;
  const { w, h } = naturalSize();
  const previous = state.zoom;
  const centreX = (viewport.scrollLeft + viewport.clientWidth / 2) / Math.max(1, w * previous);
  const centreY = (viewport.scrollTop + viewport.clientHeight / 2) / Math.max(1, h * previous);
  state.zoom = clamp(nextZoom, MIN_ZOOM, MAX_ZOOM);
  applyZoom();
  viewport.scrollLeft = centreX * w * state.zoom - viewport.clientWidth / 2;
  viewport.scrollTop = centreY * h * state.zoom - viewport.clientHeight / 2;
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
    hyp: params.get("hyp"),
    sel: params.get("sel"),
  };
}

function syncHash() {
  const params = new URLSearchParams();
  params.set("root", state.rootId);
  params.set("gen", String(state.generations));
  params.set("hyp", state.showHypotheses ? "1" : "0");
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
    li.textContent = item;
    ul.append(li);
  }
  return ul;
}

function fileLinkLabel(href) {
  const ext = href.split("?")[0].split(".").pop().toLowerCase();
  if (ext === "pdf") return "View document";
  if (["jpg", "jpeg", "png", "tif", "tiff", "gif", "webp"].includes(ext)) return "View image";
  return "View file";
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

function sourceList(sources) {
  if (!sources.length) {
    const empty = document.createElement("p");
    empty.className = "empty-note";
    empty.textContent = "No linked sources.";
    return empty;
  }

  const ul = document.createElement("ul");
  ul.className = "source-list";

  for (const source of sources) {
    const li = document.createElement("li");
    li.className = "source-item";

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
    if (source.file) actions.append(externalLink(source.file, fileLinkLabel(source.file)));
    if (source.url) actions.append(externalLink(source.url, "Source record ↗", "external"));
    if (!source.file && !source.url) {
      const none = document.createElement("span");
      none.className = "source-none";
      none.textContent = "No file retained";
      actions.append(none);
    }
    if (source.private) actions.append(createBadge("Private"));

    const nodes = [title];
    if (metaBits.length) nodes.push(meta);
    nodes.push(actions);
    if (source.transcription) {
      const transcription = document.createElement("p");
      transcription.className = "source-transcription";
      transcription.textContent = source.transcription;
      nodes.push(transcription);
    }
    if (source.abstract) {
      const abstract = document.createElement("p");
      abstract.className = "source-abstract";
      abstract.textContent = source.abstract;
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
    empty.textContent = "No context references.";
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

    const metaBits = [ref.role, ref.recordCategory, ref.place].filter(Boolean);
    const meta = document.createElement("div");
    meta.className = "source-meta";
    meta.textContent = metaBits.join(" · ");

    const actions = document.createElement("div");
    actions.className = "source-actions";
    if (ref.file) actions.append(externalLink(ref.file, fileLinkLabel(ref.file)));
    if (ref.url) actions.append(externalLink(ref.url, "Source record ↗", "external"));

    const nodes = [title];
    if (metaBits.length) nodes.push(meta);
    if (actions.childElementCount) nodes.push(actions);
    if (ref.transcription) {
      const transcription = document.createElement("p");
      transcription.className = "source-transcription";
      transcription.textContent = ref.transcription;
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

  elements.detailsId.textContent = person.id;
  elements.detailsTitle.textContent = person.name;
  elements.detailsLifespan.textContent = lifespan(person);
  elements.detailsContent.replaceChildren();

  if (person.hasConflict) {
    const caution = document.createElement("p");
    caution.className = "detail-caution";
    caution.textContent = "⚠ This record has unresolved or conflicting evidence — see the notes and sources below.";
    elements.detailsContent.append(caution);
  }

  const facts = document.createElement("dl");
  facts.className = "detail-grid";
  const factRows = [
    ["Privacy", person.privacy],
    ["Sources", String(person.sourceCount)],
    ["Context references", String((person.fanReferences || []).length)],
    ["Birthplace", person.events.find((event) => event.type === "birth")?.place?.name || "Not established"],
    ["Death place", person.events.find((event) => event.type === "death")?.place?.name || "Not established"],
  ];
  for (const [term, value] of factRows) {
    const dt = document.createElement("dt");
    dt.textContent = term;
    const dd = document.createElement("dd");
    dd.textContent = text(value);
    facts.append(dt, dd);
  }
  elements.detailsContent.append(section("Overview", facts));

  const eventItems = person.events.map((event) => {
    const place = event.place?.name ? ` · ${event.place.name}` : "";
    return `${event.type.replaceAll("_", " ")} · ${dateLabel(event)}${place} · ${statusLabels[event.status] || event.status}`;
  });
  elements.detailsContent.append(section("Events", list(eventItems, "No structured events.")));

  const parentItems = (state.data.parentsByChild[personId] || [])
    .filter(relationshipVisible)
    .map((relationship) => {
      const parent = state.data.people[relationship.parentId];
      return `${parent?.name || relationship.parentId} — ${statusLabels[relationship.status] || relationship.status}`;
    });
  elements.detailsContent.append(section("Parents", list(parentItems, "No structured parent relationship.")));

  if (person.privacy !== "living") {
    const marriageItems = person.spouses.map((spouse) => {
      const bits = [];
      const year = spouse.marriage ? yearFromEvent({ date: spouse.marriage.date }) : null;
      if (year) bits.push(`m. ${year}`);
      if (spouse.marriage?.place) bits.push(spouse.marriage.place);
      if (spouse.marriage?.status) bits.push(statusLabels[spouse.marriage.status] || spouse.marriage.status);
      return bits.length ? `${spouse.name} — ${bits.join(" · ")}` : spouse.name;
    });
    elements.detailsContent.append(section("Marriages & partners", list(marriageItems, "No recorded partners.")));

    const occupationItems = person.occupations.map((occupation) => {
      const src = occupation.sourceIds.length ? ` · ${occupation.sourceIds.join(", ")}` : "";
      return occupation.note ? `${occupation.value}${src} — ${occupation.note}` : `${occupation.value}${src}`;
    });
    elements.detailsContent.append(section("Occupation", list(occupationItems, "No recorded occupation.")));

    elements.detailsContent.append(section("Recorded names", list(person.nameVariants, "No name variants.")));
    elements.detailsContent.append(section("Sources", sourceList(person.sources)));
    elements.detailsContent.append(
      section("Context references (FAN)", fanList(person.fanReferences || [])),
    );
    elements.detailsContent.append(section("Research notes", list(person.notes, "No public research notes.")));
  } else {
    const privacy = document.createElement("p");
    privacy.className = "empty-note";
    privacy.textContent = "Details are intentionally minimised for living people.";
    elements.detailsContent.append(section("Privacy", privacy));
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
  elements.detailsPanel.hidden = true;
  elements.backdrop.hidden = true;
  state.selected = null;
  syncHash();
  if (lastFocused && lastFocused.isConnected && typeof lastFocused.focus === "function") {
    lastFocused.focus();
  }
  lastFocused = null;
}

function bindEvents() {
  elements.rootSelect.addEventListener("change", () => {
    state.rootId = elements.rootSelect.value;
    state.autoFit = true;
    renderTree();
    syncHash();
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
    if (!(event.ctrlKey || event.metaKey)) return;
    event.preventDefault();
    state.autoFit = false;
    setZoom(state.zoom * (event.deltaY < 0 ? 1.1 : 1 / 1.1));
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

  elements.showHypotheses.addEventListener("change", () => {
    state.showHypotheses = elements.showHypotheses.checked;
    renderTree();
    syncHash();
  });

  elements.search.addEventListener("input", () => {
    populatePersonSelect(elements.search.value);
  });

  elements.search.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && elements.rootSelect.options.length) {
      state.rootId = elements.rootSelect.options[0].value;
      populatePersonSelect("");
      elements.search.value = "";
      elements.rootSelect.value = state.rootId;
      state.autoFit = true;
      renderTree();
      syncHash();
    }
  });

  elements.reset.addEventListener("click", () => {
    state.rootId = state.data.people["P-0001"] ? "P-0001" : Object.keys(state.data.people)[0];
    state.generations = 4;
    state.showHypotheses = true;
    state.autoFit = true;
    elements.generationLimit.value = "4";
    elements.showHypotheses.checked = true;
    elements.search.value = "";
    populatePersonSelect();
    elements.rootSelect.value = state.rootId;
    renderTree();
    syncHash();
  });

  elements.closeDetails.addEventListener("click", closeDetails);
  elements.backdrop.addEventListener("click", closeDetails);
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !elements.detailsPanel.hidden) closeDetails();
  });
}

async function initialise() {
  bindEvents();
  try {
    const response = await fetch("/api/tree", { cache: "no-store" });
    if (!response.ok) throw new Error(`The data service returned HTTP ${response.status}.`);
    state.data = await response.json();
    state.rootId = state.data.people["P-0001"] ? "P-0001" : Object.keys(state.data.people)[0];

    // Restore a shared/bookmarked view from the URL hash.
    const hash = readHash();
    if (hash.root && state.data.people[hash.root]) state.rootId = hash.root;
    if (hash.gen && /^[2-8]$/.test(hash.gen)) state.generations = Number(hash.gen);
    if (hash.hyp === "0") state.showHypotheses = false;

    populatePersonSelect();
    elements.rootSelect.value = state.rootId;
    elements.generationLimit.value = String(state.generations);
    elements.showHypotheses.checked = state.showHypotheses;
    elements.personCount.textContent = String(Object.keys(state.data.people).length);
    elements.familyCount.textContent = String(state.data.familyCount);
    elements.sourceCount.textContent = String(Object.keys(state.data.sources).length);
    elements.loading.hidden = true;
    renderTree();
    if (hash.sel && state.data.people[hash.sel]) openDetails(hash.sel);
    else syncHash();
  } catch (error) {
    elements.loading.hidden = true;
    elements.error.hidden = false;
    elements.error.textContent = `Unable to load the family tree: ${error.message}`;
  }
}

initialise();
