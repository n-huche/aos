#!/usr/bin/env node
// Vault validator: enforces the conventions declared in AGENTS.md.
//
// Checks:
//   1. No `[[wiki]]` links (AGENTS.md requires `[name](relative path)`).
//   2. Every relative Markdown link resolves to an existing file.
//   3. File and folder names are kebab-case ASCII, no spaces ("inglês, kebab-case, ASCII").
//   4. No empty folders ("Pasta só com nota" — a folder must hold a note).
//
// Exit code is non-zero when any error is found, so it can gate CI / pre-commit.

import { readdirSync, readFileSync, statSync } from "node:fs";
import { join, relative, dirname, resolve, basename, sep } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = resolve(fileURLToPath(import.meta.url), "..", "..");

// Paths (relative to ROOT) that are tooling/config, not vault content.
const IGNORED_DIRS = new Set([".git", "node_modules", ".obsidian", ".cursor", "scripts"]);
// Basenames allowed to break the kebab-case rule (project-level config & docs).
const NAME_WHITELIST = new Set([
  "AGENTS.md",
  "README.md",
  "LICENSE",
  "package.json",
  "package-lock.json",
  ".gitignore",
  ".markdownlint-cli2.jsonc",
]);

const KEBAB = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;

// Link/wiki-link checks apply only to real vault content. The `agents/` engine
// docs and root AGENTS.md intentionally contain link *patterns* with placeholders
// ({slug}, ../{{slug}}.md) and even the literal `[[wiki]]` shown as a bad example.
const CONTENT_ROOTS = new Set(["tasks", "projects", "daily"]);

function isContent(rel) {
  return CONTENT_ROOTS.has(rel.split(sep)[0]);
}

const errors = [];
const stats = { files: 0, dirs: 0, links: 0 };

function isIgnored(relPath) {
  const first = relPath.split(sep)[0];
  return IGNORED_DIRS.has(first) || relPath.startsWith(".");
}

/** Recursively collect every file and directory under the vault, skipping tooling paths. */
function walk(dir, onFile, onDir) {
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const abs = join(dir, entry.name);
    const rel = relative(ROOT, abs);
    if (isIgnored(rel)) continue;
    if (entry.isDirectory()) {
      onDir(abs, rel, entry.name);
      walk(abs, onFile, onDir);
    } else if (entry.isFile()) {
      onFile(abs, rel, entry.name);
    }
  }
}

/** Rule 3: names must be kebab-case ASCII (English), no spaces. */
function checkName(rel, name, kind) {
  if (NAME_WHITELIST.has(name)) return;
  const stem = name.endsWith(".md") ? name.slice(0, -3) : name;
  if (!KEBAB.test(stem)) {
    errors.push(`${rel}: ${kind} name "${name}" is not kebab-case ASCII (AGENTS.md: inglês, kebab-case, ASCII, sem espaços)`);
  }
}

/** Rules 1 & 2: link hygiene inside a Markdown file. */
function checkLinks(abs, rel) {
  const text = readFileSync(abs, "utf8");
  const lines = text.split(/\r?\n/);

  lines.forEach((line, i) => {
    if (line.includes("[[") && line.includes("]]")) {
      errors.push(`${rel}:${i + 1}: uses [[wiki]] link — AGENTS.md requires [nome](caminho relativo)`);
    }
  });

  // Markdown links: [text](target). Excludes bare autolinks; titles are stripped.
  const linkRe = /\[[^\]]*\]\(([^)]+)\)/g;
  let m;
  while ((m = linkRe.exec(text)) !== null) {
    let target = m[1].trim();
    // Strip an optional link title: (path "title").
    target = target.replace(/\s+["'].*$/s, "").trim();
    if (!target) continue;
    if (/^[a-z][a-z0-9+.-]*:/i.test(target)) continue; // scheme: http, https, mailto, tel...
    if (target.startsWith("#")) continue; // in-page anchor
    stats.links++;
    const path = target.split("#")[0].split("?")[0];
    if (!path) continue;
    const resolved = resolve(dirname(abs), path);
    let ok = true;
    try {
      statSync(resolved);
    } catch {
      ok = false;
    }
    if (!ok) {
      const upto = text.slice(0, m.index);
      const line = upto.split(/\r?\n/).length;
      errors.push(`${rel}:${line}: broken relative link -> "${target}" (resolved: ${relative(ROOT, resolved)})`);
    }
  }
}

// --- Walk the vault -------------------------------------------------------

const dirHasMarkdown = new Map();

walk(
  ROOT,
  (abs, rel, name) => {
    stats.files++;
    checkName(rel, name, "file");
    if (name.endsWith(".md")) {
      if (isContent(rel)) checkLinks(abs, rel);
      // Mark this dir and all ancestors as containing a note.
      let d = dirname(abs);
      while (d.startsWith(ROOT) && d !== ROOT) {
        dirHasMarkdown.set(d, true);
        d = dirname(d);
      }
    }
  },
  (abs, rel, name) => {
    stats.dirs++;
    checkName(rel, name, "folder");
    if (!dirHasMarkdown.has(abs)) dirHasMarkdown.set(abs, false);
  },
);

// Rule 4: a folder must contain a note somewhere in its subtree.
for (const [abs, hasMd] of dirHasMarkdown) {
  if (!hasMd) {
    errors.push(`${relative(ROOT, abs)}: empty folder (AGENTS.md: "Pasta só com nota")`);
  }
}

// --- Report ---------------------------------------------------------------

console.log(`Vault validator — scanned ${stats.files} files, ${stats.dirs} folders, ${stats.links} internal links`);
if (errors.length === 0) {
  console.log("PASS: vault obeys its conventions (kebab-case names, resolvable relative links, no wiki links, no empty folders).");
  process.exit(0);
} else {
  console.error(`\nFAIL: ${errors.length} problem(s) found:\n`);
  for (const e of errors.sort()) console.error(`  - ${e}`);
  process.exit(1);
}
