"use strict";

const state = {
  data: null,
  rootId: "P-0001",
  generations: 4,
  showHypotheses: true,
  visibleNodes: 0,
};

const elements = {
  rootSelect: document.querySelector("#root-person"),
  generationLimit: document.querySelector("#generation-limit"),
  search: document.querySelector("#person-search"),
  showHypotheses: document.querySelector("#show-hypotheses"),
  reset: document.querySelector("#reset-view"),
  loading: document.querySelector("#loading"),
  error: document.querySelector("#error"),
  tree: document.querySelector("#tree"),
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
  button.addEventListener("click", () => openDetails(person.id));
  return button;
}

function createGenerationStop() {
  const stop = document.createElement("div");
  stop.className = "generation-stop";
  stop.textContent = "Generation limit reached";
  return stop;
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

function openDetails(personId) {
  const person = state.data.people[personId];
  if (!person) return;

  elements.detailsId.textContent = person.id;
  elements.detailsTitle.textContent = person.name;
  elements.detailsLifespan.textContent = lifespan(person);
  elements.detailsContent.replaceChildren();

  const facts = document.createElement("dl");
  facts.className = "detail-grid";
  const factRows = [
    ["Privacy", person.privacy],
    ["Sources", String(person.sourceCount)],
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
    elements.detailsContent.append(section("Recorded names", list(person.nameVariants, "No name variants.")));
    const sourceItems = person.sources.map((source) => `${source.id} — ${source.title}`);
    elements.detailsContent.append(section("Sources", list(sourceItems, "No linked sources.")));
    elements.detailsContent.append(section("Research notes", list(person.notes, "No public research notes.")));
  } else {
    const privacy = document.createElement("p");
    privacy.className = "empty-note";
    privacy.textContent = "Details are intentionally minimised for living people.";
    elements.detailsContent.append(section("Privacy", privacy));
  }

  elements.detailsPanel.hidden = false;
  elements.backdrop.hidden = false;
  elements.closeDetails.focus();
}

function closeDetails() {
  elements.detailsPanel.hidden = true;
  elements.backdrop.hidden = true;
}

function bindEvents() {
  elements.rootSelect.addEventListener("change", () => {
    state.rootId = elements.rootSelect.value;
    renderTree();
  });

  elements.generationLimit.addEventListener("change", () => {
    state.generations = Number(elements.generationLimit.value);
    renderTree();
  });

  elements.showHypotheses.addEventListener("change", () => {
    state.showHypotheses = elements.showHypotheses.checked;
    renderTree();
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
      renderTree();
    }
  });

  elements.reset.addEventListener("click", () => {
    state.rootId = state.data.people["P-0001"] ? "P-0001" : Object.keys(state.data.people)[0];
    state.generations = 4;
    state.showHypotheses = true;
    elements.generationLimit.value = "4";
    elements.showHypotheses.checked = true;
    elements.search.value = "";
    populatePersonSelect();
    elements.rootSelect.value = state.rootId;
    renderTree();
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

    populatePersonSelect();
    elements.rootSelect.value = state.rootId;
    elements.personCount.textContent = String(Object.keys(state.data.people).length);
    elements.familyCount.textContent = String(state.data.familyCount);
    elements.sourceCount.textContent = String(Object.keys(state.data.sources).length);
    elements.loading.hidden = true;
    renderTree();
  } catch (error) {
    elements.loading.hidden = true;
    elements.error.hidden = false;
    elements.error.textContent = `Unable to load the family tree: ${error.message}`;
  }
}

initialise();
