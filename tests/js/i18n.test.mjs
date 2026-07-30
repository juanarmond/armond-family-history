// Unit tests for the pure i18n logic in family-tree-viewer/i18n.js.
// Run directly with `node --test tests/js/`, or via tests/test_data_loader_js.py
// inside `make check`.

import test from "node:test";
import assert from "node:assert/strict";

import {
  createI18n,
  resolveLocale,
  SUPPORTED_LOCALES,
  DEFAULT_LOCALE,
  STRINGS,
  VOCAB,
} from "../../family-tree-viewer/i18n.js";

test("resolveLocale maps Portuguese variants to pt-BR", () => {
  assert.equal(resolveLocale("pt-BR"), "pt-BR");
  assert.equal(resolveLocale("pt"), "pt-BR");
  assert.equal(resolveLocale("pt-PT"), "pt-BR");
  assert.equal(resolveLocale(["pt-BR", "en"]), "pt-BR");
});

test("resolveLocale maps English variants to en", () => {
  assert.equal(resolveLocale("en"), "en");
  assert.equal(resolveLocale("en-US"), "en");
  assert.equal(resolveLocale(["en-GB", "pt-BR"]), "en", "the first recognised entry wins");
});

test("resolveLocale falls back to English when neither is obviously set", () => {
  assert.equal(resolveLocale("fr-FR"), "en");
  assert.equal(resolveLocale([]), "en");
  assert.equal(resolveLocale([null, undefined, ""]), "en");
  assert.equal(resolveLocale(undefined), "en");
  assert.equal(DEFAULT_LOCALE, "en");
});

test("t interpolates and falls back to English then to the key", () => {
  const en = createI18n("en");
  const pt = createI18n("pt-BR");
  assert.equal(en.t("detail.sources"), "Sources");
  assert.equal(pt.t("detail.sources"), "Fontes");
  assert.equal(pt.t("card.aria", { name: "Ann" }), "Abrir detalhes de Ann");
  assert.equal(en.t("does.not.exist"), "does.not.exist");
});

test("tn selects singular vs plural", () => {
  const pt = createI18n("pt-BR");
  assert.equal(pt.tn("badge.source", 1, { n: 1 }), "1 fonte");
  assert.equal(pt.tn("badge.source", 3, { n: 3 }), "3 fontes");
});

test("label translates controlled vocabulary and humanises unknowns", () => {
  const pt = createI18n("pt-BR");
  assert.equal(pt.label("status", "confirmed"), "Confirmado");
  assert.equal(pt.label("event", "marriage"), "casamento");
  assert.equal(pt.label("privacy", "deceased"), "falecida");
  assert.equal(pt.label("event", "land_transfer"), "land transfer", "unmapped enum -> humanised raw value");
});

test("an unsupported locale falls back to the default", () => {
  const x = createI18n("fr");
  assert.equal(x.locale, DEFAULT_LOCALE);
  assert.equal(x.t("detail.sources"), "Sources");
});

test("pt-BR defines the same keys as en (no missing translations)", () => {
  assert.deepEqual(Object.keys(STRINGS["pt-BR"]).sort(), Object.keys(STRINGS.en).sort());
  assert.deepEqual(Object.keys(VOCAB["pt-BR"]).sort(), Object.keys(VOCAB.en).sort());
  assert.deepEqual(SUPPORTED_LOCALES, ["en", "pt-BR"]);
});
