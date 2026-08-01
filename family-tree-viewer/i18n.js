// Dependency-free i18n for the viewer. English is the base/fallback locale;
// pt-BR (Brazilian Portuguese) is the alternate. No DOM or window access here,
// so the logic is unit-testable under Node (see tests/js/i18n.test.mjs).
//
// This layer translates only the UI chrome and controlled-vocabulary labels
// (event types, relationship statuses, privacy). It never translates the
// genealogical data itself — names, transcriptions, places and record types
// display exactly as recorded.

export const SUPPORTED_LOCALES = ["en", "pt-BR"];
export const DEFAULT_LOCALE = "en";

// Resolve a preferred language (a string or an ordered list such as
// navigator.languages) to a supported locale. Anything obviously Portuguese
// resolves to "pt-BR"; anything else — including unset or unrecognised — falls
// back to English.
export function resolveLocale(preferred) {
  const list = Array.isArray(preferred) ? preferred : [preferred];
  for (const raw of list) {
    if (typeof raw !== "string" || !raw.trim()) continue;
    const lower = raw.trim().toLowerCase();
    if (lower === "pt" || lower.startsWith("pt-") || lower.startsWith("pt_")) return "pt-BR";
    if (lower === "en" || lower.startsWith("en-") || lower.startsWith("en_")) return "en";
  }
  return DEFAULT_LOCALE;
}

// UI chrome strings. Keys are stable ids; `{name}` etc. are interpolated.
const STRINGS = {
  en: {
    "page.title": "Armond Family History",
    "header.eyebrow": "Private research archive",
    "header.subtitle":
      "Evidence-led ancestral tree generated directly from the repository's validated YAML records.",
    "header.emblem": "Armond Family History emblem: a family-tree seal",
    "toolbar.aria": "Tree controls",
    "control.startPerson": "Start person",
    "control.generations": "Generations",
    "control.findPerson": "Find a person",
    "control.searchPlaceholder": "Search by name",
    "control.showHypotheses": "Show hypotheses",
    "control.reset": "Reset view",
    "control.language": "Language",
    "summary.aria": "Repository summary",
    "summary.people": "people",
    "summary.families": "families",
    "summary.sources": "sources",
    "summary.visible": "visible nodes",
    "zoom.aria": "Zoom controls",
    "zoom.out": "Zoom out",
    "zoom.in": "Zoom in",
    "zoom.fit": "Fit",
    "loading": "Loading the family archive…",
    "panel.close": "Close person details",
    "footer": "Read-only static visualisation. Repository YAML remains the canonical source of truth.",
    "date.unknown": "Unknown date",
    "text.unknown": "Unknown",
    "lifespan.living": "Living person",
    "lifespan.unknown": "Dates not established",
    "place.unknown": "Place not established",
    "card.aria": "Open details for {name}",
    "card.title": "Click for details · double-click to centre the tree here",
    "badge.source.one": "{n} source",
    "badge.source.other": "{n} sources",
    "badge.conflict": "Conflict",
    "badge.private": "Private",
    "tree.generationStop": "Generation limit reached",
    "tree.personUnavailable": "Person {id} is not available.",
    "marriage.label": "Marriage",
    "marriage.year": "m. {year}",
    "detail.overview": "Overview",
    "detail.events": "Events",
    "detail.parents": "Parents",
    "detail.siblings": "Siblings",
    "detail.children": "Children",
    "detail.marriages": "Marriages & partners",
    "detail.occupation": "Occupation",
    "detail.recordedNames": "Recorded names",
    "detail.sources": "Sources",
    "detail.fan": "Context references (FAN)",
    "detail.notes": "Research notes",
    "detail.privacy": "Privacy",
    "detail.caution":
      "⚠ This record has sources with uncertain or unresolved readings — they are marked ⚠ below.",
    "detail.livingMinimised": "Details are intentionally minimised for living people.",
    "fact.privacy": "Privacy",
    "fact.sources": "Sources",
    "fact.contextRefs": "Context references",
    "fact.birthplace": "Birthplace",
    "fact.nationality": "Nationality",
    "fact.deathplace": "Death place",
    "value.notEstablished": "Not established",
    "empty.events": "No structured events.",
    "empty.parents": "No structured parent relationship.",
    "empty.siblings": "No documented siblings.",
    "empty.children": "No documented children.",
    "empty.partners": "No recorded partners.",
    "empty.occupation": "No recorded occupation.",
    "empty.names": "No name variants.",
    "empty.notes": "No public research notes.",
    "empty.sources": "No linked sources.",
    "empty.fan": "No context references.",
    "file.viewDocument": "View document",
    "file.viewImage": "View image",
    "file.viewFile": "View file",
    "source.recordLink": "Source record ↗",
    "source.noFile": "No file retained",
    "source.uncertain": "Uncertain reading",
    "reader.open": "Read document ⤢",
    "reader.close": "Close",
    "reader.transcription": "Transcription",
    "reader.abstract": "Abstract",
    "reader.noTranscript": "No transcription.",
    "reader.zoomHint": "Scroll to zoom · drag to pan · double-click to reset",
    "detail.biography": "Biography",
    "bio.months": "January|February|March|April|May|June|July|August|September|October|November|December",
    "bio.dateExact": "on {d} {m} {y}",
    "bio.dateMonth": "in {m} {y}",
    "bio.dateYear": "in {y}",
    "bio.dateAbout": "in about {y}",
    "bio.dateBefore": "before {y}",
    "bio.dateAfter": "after {y}",
    "bio.inPlace": "in {place}",
    "list.and": "and",
    "bio.pronMale": "He",
    "bio.pronFemale": "She",
    "bio.born": "{subject} was born{when}{where}{parents}.",
    "bio.sonOf": ", a son of {parents}",
    "bio.daughterOf": ", a daughter of {parents}",
    "bio.childOf": ", a child of {parents}",
    "bio.emigrated": "{subject} later emigrated to Brazil.",
    "bio.married": "{subject} married {spouse}{when}{where}.",
    "bio.children": "The recorded children were {names}.",
    "bio.parentOfFather": "{subject} is recorded as the father of {names}.",
    "bio.parentOfMother": "{subject} is recorded as the mother of {names}.",
    "bio.parentOfParent": "{subject} is recorded as a parent of {names}.",
    "bio.worked": "{subject} worked as {occupations}.",
    "bio.died": "{subject} died{when}{where}{age}.",
    "bio.age": ", aged {n}",
    "bio.ageApprox": ", aged about {n}",
    "bio.sparse": "Few records of {name}'s own life have been located.",
    "detail.relationship": "Relationship to {name}",
    "rel.father": "father",
    "rel.mother": "mother",
    "rel.parentNeutral": "parent",
    "rel.grandfather": "grandfather",
    "rel.grandmother": "grandmother",
    "rel.grandparentNeutral": "grandparent",
    "rel.greatGrandfather": "great-grandfather",
    "rel.greatGrandmother": "great-grandmother",
    "rel.greatGrandparentNeutral": "great-grandparent",
    "rel.ancestorDeep": "direct ancestor",
    "rel.generations": "({n} generations back)",
    "rel.paternalLine": "paternal line",
    "rel.maternalLine": "maternal line",
    "rel.related": "relative",
    "error.httpStatus": "The data service returned HTTP {status}.",
    "error.loadFailed": "Unable to load the family tree: {message}",
  },
  "pt-BR": {
    "page.title": "História da Família Armond",
    "header.eyebrow": "Arquivo de pesquisa privado",
    "header.subtitle":
      "Árvore genealógica baseada em evidências, gerada diretamente dos registros YAML validados do repositório.",
    "header.emblem": "Emblema da História da Família Armond: um selo de árvore genealógica",
    "toolbar.aria": "Controles da árvore",
    "control.startPerson": "Pessoa inicial",
    "control.generations": "Gerações",
    "control.findPerson": "Buscar pessoa",
    "control.searchPlaceholder": "Buscar por nome",
    "control.showHypotheses": "Mostrar hipóteses",
    "control.reset": "Redefinir visualização",
    "control.language": "Idioma",
    "summary.aria": "Resumo do repositório",
    "summary.people": "pessoas",
    "summary.families": "famílias",
    "summary.sources": "fontes",
    "summary.visible": "nós visíveis",
    "zoom.aria": "Controles de zoom",
    "zoom.out": "Diminuir zoom",
    "zoom.in": "Aumentar zoom",
    "zoom.fit": "Ajustar",
    "loading": "Carregando o arquivo da família…",
    "panel.close": "Fechar detalhes da pessoa",
    "footer": "Visualização estática, somente leitura. O YAML do repositório continua sendo a fonte canônica da verdade.",
    "date.unknown": "Data desconhecida",
    "text.unknown": "Desconhecido",
    "lifespan.living": "Pessoa viva",
    "lifespan.unknown": "Datas não estabelecidas",
    "place.unknown": "Local não estabelecido",
    "card.aria": "Abrir detalhes de {name}",
    "card.title": "Clique para ver detalhes · clique duplo para centralizar a árvore aqui",
    "badge.source.one": "{n} fonte",
    "badge.source.other": "{n} fontes",
    "badge.conflict": "Conflito",
    "badge.private": "Privado",
    "tree.generationStop": "Limite de gerações atingido",
    "tree.personUnavailable": "A pessoa {id} não está disponível.",
    "marriage.label": "Casamento",
    "marriage.year": "cas. {year}",
    "detail.overview": "Visão geral",
    "detail.events": "Eventos",
    "detail.parents": "Pais",
    "detail.siblings": "Irmãos",
    "detail.children": "Filhos",
    "detail.marriages": "Casamentos e cônjuges",
    "detail.occupation": "Ocupação",
    "detail.recordedNames": "Nomes registrados",
    "detail.sources": "Fontes",
    "detail.fan": "Referências de contexto (FAN)",
    "detail.notes": "Notas de pesquisa",
    "detail.privacy": "Privacidade",
    "detail.caution":
      "⚠ Este registro tem fontes com leituras incertas ou não resolvidas — marcadas com ⚠ abaixo.",
    "detail.livingMinimised": "Os detalhes são intencionalmente minimizados para pessoas vivas.",
    "fact.privacy": "Privacidade",
    "fact.sources": "Fontes",
    "fact.contextRefs": "Referências de contexto",
    "fact.birthplace": "Local de nascimento",
    "fact.nationality": "Nacionalidade",
    "fact.deathplace": "Local de falecimento",
    "value.notEstablished": "Não estabelecido",
    "empty.events": "Nenhum evento estruturado.",
    "empty.parents": "Nenhuma relação de filiação estruturada.",
    "empty.siblings": "Nenhum irmão documentado.",
    "empty.children": "Nenhum filho documentado.",
    "empty.partners": "Nenhum cônjuge registrado.",
    "empty.occupation": "Nenhuma ocupação registrada.",
    "empty.names": "Nenhuma variante de nome.",
    "empty.notes": "Nenhuma nota de pesquisa pública.",
    "empty.sources": "Nenhuma fonte vinculada.",
    "empty.fan": "Nenhuma referência de contexto.",
    "file.viewDocument": "Ver documento",
    "file.viewImage": "Ver imagem",
    "file.viewFile": "Ver arquivo",
    "source.recordLink": "Registro da fonte ↗",
    "source.noFile": "Nenhum arquivo retido",
    "source.uncertain": "Leitura incerta",
    "reader.open": "Ler documento ⤢",
    "reader.close": "Fechar",
    "reader.transcription": "Transcrição",
    "reader.abstract": "Resumo",
    "reader.noTranscript": "Sem transcrição.",
    "reader.zoomHint": "Role para ampliar · arraste para mover · duplo-clique para redefinir",
    "detail.biography": "Biografia",
    "bio.months": "janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro",
    "bio.dateExact": "em {d} de {m} de {y}",
    "bio.dateMonth": "em {m} de {y}",
    "bio.dateYear": "em {y}",
    "bio.dateAbout": "por volta de {y}",
    "bio.dateBefore": "antes de {y}",
    "bio.dateAfter": "depois de {y}",
    "bio.inPlace": "em {place}",
    "list.and": "e",
    "bio.pronMale": "Ele",
    "bio.pronFemale": "Ela",
    "bio.born": "{subject} nasceu{when}{where}{parents}.",
    "bio.sonOf": ", filho de {parents}",
    "bio.daughterOf": ", filha de {parents}",
    "bio.childOf": ", filho(a) de {parents}",
    "bio.emigrated": "{subject} mais tarde emigrou para o Brasil.",
    "bio.married": "{subject} casou-se com {spouse}{when}{where}.",
    "bio.children": "Os filhos registrados foram {names}.",
    "bio.parentOfFather": "{subject} consta como pai de {names}.",
    "bio.parentOfMother": "{subject} consta como mãe de {names}.",
    "bio.parentOfParent": "{subject} consta como progenitor(a) de {names}.",
    "bio.worked": "{subject} trabalhou como {occupations}.",
    "bio.died": "{subject} faleceu{when}{where}{age}.",
    "bio.age": ", aos {n} anos",
    "bio.ageApprox": ", com cerca de {n} anos",
    "bio.sparse": "Poucos registros da própria vida de {name} foram localizados.",
    "detail.relationship": "Parentesco com {name}",
    "rel.father": "pai",
    "rel.mother": "mãe",
    "rel.parentNeutral": "ascendente",
    "rel.grandfather": "avô",
    "rel.grandmother": "avó",
    "rel.grandparentNeutral": "avô/avó",
    "rel.greatGrandfather": "bisavô",
    "rel.greatGrandmother": "bisavó",
    "rel.greatGrandparentNeutral": "bisavô/bisavó",
    "rel.ancestorDeep": "ascendente direto",
    "rel.generations": "({n} gerações)",
    "rel.paternalLine": "linha paterna",
    "rel.maternalLine": "linha materna",
    "rel.related": "parente",
    "error.httpStatus": "O serviço de dados retornou HTTP {status}.",
    "error.loadFailed": "Não foi possível carregar a árvore genealógica: {message}",
  },
};

// Controlled-vocabulary labels. Falls back to the English label, then to a
// humanised form of the raw value, so an unmapped enum still renders sensibly.
const VOCAB = {
  en: {
    "status.confirmed": "Confirmed",
    "status.strong-evidence": "Strong evidence",
    "status.hypothesis": "Hypothesis",
    "status.rejected": "Rejected",
    "status.unknown": "Unspecified",
    "privacy.living": "living",
    "privacy.deceased": "deceased",
    "privacy.unknown": "unknown",
    "event.birth": "birth",
    "event.death": "death",
    "event.marriage": "marriage",
    "event.baptism": "baptism",
    "event.burial": "burial",
    "event.residence": "residence",
    "event.census": "census",
    "event.immigration": "immigration",
    "event.naturalisation": "naturalisation",
    "event.occupation": "occupation",
    "event.other": "other",
  },
  "pt-BR": {
    "status.confirmed": "Confirmado",
    "status.strong-evidence": "Evidência forte",
    "status.hypothesis": "Hipótese",
    "status.rejected": "Rejeitado",
    "status.unknown": "Não especificado",
    "privacy.living": "viva",
    "privacy.deceased": "falecida",
    "privacy.unknown": "desconhecida",
    "event.birth": "nascimento",
    "event.death": "falecimento",
    "event.marriage": "casamento",
    "event.baptism": "batismo",
    "event.burial": "sepultamento",
    "event.residence": "residência",
    "event.census": "censo",
    "event.immigration": "imigração",
    "event.naturalisation": "naturalização",
    "event.occupation": "ocupação",
    "event.other": "outro",
  },
};

function humanise(value) {
  return typeof value === "string" ? value.replaceAll("_", " ") : String(value ?? "");
}

function interpolate(template, vars) {
  if (!vars) return template;
  let out = template;
  for (const [key, value] of Object.entries(vars)) {
    out = out.replaceAll(`{${key}}`, String(value));
  }
  return out;
}

// Build a translator bound to a locale. `t(key, vars)` for UI strings;
// `tn(key, n, vars)` for count-sensitive strings (`key.one` / `key.other`);
// `label(kind, value)` for controlled vocabulary.
export function createI18n(locale) {
  const loc = SUPPORTED_LOCALES.includes(locale) ? locale : DEFAULT_LOCALE;
  const table = STRINGS[loc];
  const vocab = VOCAB[loc];

  const t = (key, vars) => interpolate(table[key] ?? STRINGS.en[key] ?? key, vars);
  const tn = (key, n, vars) => t(`${key}.${n === 1 ? "one" : "other"}`, { n, ...(vars || {}) });
  const label = (kind, value) => {
    const key = `${kind}.${value}`;
    return vocab[key] ?? VOCAB.en[key] ?? humanise(value);
  };

  return { locale: loc, t, tn, label };
}

export { STRINGS, VOCAB };
