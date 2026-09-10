#!/usr/bin/env node
// Markdown preview server for the vault.
//
// Renders any `.md` note to HTML on the fly and rewrites relative links so the
// whole vault is browsable in a web browser (a headless stand-in for Obsidian).
//
//   PORT=8080 node scripts/preview-server.mjs
//
// Routes:
//   /                      -> vault home (tree of folders and notes)
//   /view/<relative-path>  -> a rendered Markdown note
//   /raw/<relative-path>   -> a raw file (images, etc.)

import { createServer } from "node:http";
import { readFileSync, statSync, readdirSync } from "node:fs";
import { join, relative, dirname, resolve, sep, extname, posix } from "node:path";
import { fileURLToPath } from "node:url";
import { marked } from "marked";

const ROOT = resolve(fileURLToPath(import.meta.url), "..", "..");
const PORT = Number(process.env.PORT) || 8080;
const HOST = process.env.HOST || "0.0.0.0";
const IGNORED = new Set([".git", "node_modules", ".obsidian", ".cursor", "scripts"]);

marked.setOptions({ gfm: true, breaks: false });

const PAGE = (title, body) => `<!doctype html>
<html lang="pt-BR"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>${escapeHtml(title)} · Vault</title>
<style>
  :root { color-scheme: light dark; }
  * { box-sizing: border-box; }
  body { margin: 0; font: 16px/1.6 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
         color: #1f2328; background: #ffffff; }
  header { position: sticky; top: 0; background: #0d1117; color: #e6edf3; padding: 12px 24px;
           display: flex; gap: 16px; align-items: center; box-shadow: 0 1px 0 rgba(0,0,0,.15); }
  header a { color: #7ee787; text-decoration: none; font-weight: 600; }
  header a:hover { text-decoration: underline; }
  header .brand { color: #e6edf3; font-weight: 700; margin-right: auto; }
  main { max-width: 900px; margin: 0 auto; padding: 32px 24px 80px; }
  a { color: #0969da; }
  h1, h2, h3 { line-height: 1.25; }
  h1 { border-bottom: 1px solid #d0d7de; padding-bottom: .3em; }
  h2 { border-bottom: 1px solid #d0d7de; padding-bottom: .3em; margin-top: 2em; }
  code { background: rgba(175,184,193,.2); padding: .2em .4em; border-radius: 6px; font-size: 85%; }
  pre code { display: block; padding: 16px; overflow: auto; }
  table { border-collapse: collapse; width: 100%; margin: 1em 0; display: block; overflow: auto; }
  th, td { border: 1px solid #d0d7de; padding: 6px 13px; }
  tr:nth-child(2n) { background: #f6f8fa; }
  ul.tree { list-style: none; padding-left: 18px; }
  ul.tree li { margin: 2px 0; }
  .dir { font-weight: 600; }
  .muted { color: #656d76; }
  blockquote { border-left: 4px solid #d0d7de; margin: 0; padding: 0 1em; color: #656d76; }
</style></head><body>
<header>
  <span class="brand">docs vault</span>
  <a href="/">Home</a>
  <a href="/view/AGENTS.md">AGENTS</a>
  <a href="/view/projects/projects.md">Projetos</a>
  <a href="/view/tasks/tasks.md">Tarefas</a>
</header>
<main>${body}</main>
</body></html>`;

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

function safeResolve(relPath) {
  const abs = resolve(ROOT, "." + sep + relPath);
  if (abs !== ROOT && !abs.startsWith(ROOT + sep)) return null; // block path traversal
  return abs;
}

/** Rewrite relative links in rendered HTML so navigation stays inside the preview. */
function rewriteLinks(html, fileRel) {
  const baseDir = dirname(fileRel);
  return html.replace(/(href|src)="([^"]*)"/g, (full, attr, url) => {
    if (/^[a-z][a-z0-9+.-]*:/i.test(url) || url.startsWith("//") || url.startsWith("#") || url.startsWith("/")) {
      return full;
    }
    const [pathPart, hash = ""] = url.split("#");
    const targetRel = posix.normalize(posix.join(baseDir.split(sep).join("/"), pathPart));
    const route = extname(pathPart).toLowerCase() === ".md" ? "/view/" : "/raw/";
    return `${attr}="${route}${targetRel}${hash ? "#" + hash : ""}"`;
  });
}

function renderMarkdown(abs, rel) {
  const md = readFileSync(abs, "utf8");
  const html = rewriteLinks(marked.parse(md), rel);
  const parent = dirname(rel);
  const crumb = parent && parent !== "."
    ? `<p class="muted">${escapeHtml(rel)}</p>`
    : `<p class="muted">${escapeHtml(rel)}</p>`;
  return PAGE(rel, crumb + html);
}

function renderHome() {
  function listDir(absDir, relDir) {
    const entries = readdirSync(absDir, { withFileTypes: true })
      .filter((e) => !(relDir === "" && IGNORED.has(e.name)) && !e.name.startsWith("."))
      .sort((a, b) => (a.isDirectory() === b.isDirectory() ? a.name.localeCompare(b.name) : a.isDirectory() ? -1 : 1));
    let out = "<ul class='tree'>";
    for (const e of entries) {
      const childRel = relDir ? `${relDir}/${e.name}` : e.name;
      if (e.isDirectory()) {
        out += `<li><span class="dir">${escapeHtml(e.name)}/</span>${listDir(join(absDir, e.name), childRel)}</li>`;
      } else if (e.name.endsWith(".md")) {
        out += `<li><a href="/view/${childRel}">${escapeHtml(e.name)}</a></li>`;
      }
    }
    return out + "</ul>";
  }
  const body = `<h1>docs vault</h1>
<p class="muted">Sistema de tarefas, projetos e diário em Markdown. Navegue pelas notas abaixo.</p>
${listDir(ROOT, "")}`;
  return PAGE("Home", body);
}

const server = createServer((req, res) => {
  try {
    const url = decodeURIComponent(req.url.split("?")[0]);
    if (url === "/" || url === "") {
      res.writeHead(200, { "content-type": "text/html; charset=utf-8" });
      return res.end(renderHome());
    }
    if (url === "/healthz") {
      res.writeHead(200, { "content-type": "text/plain" });
      return res.end("ok");
    }
    const m = url.match(/^\/(view|raw)\/(.+)$/);
    if (m) {
      const [, mode, relPath] = m;
      const abs = safeResolve(relPath);
      if (!abs) {
        res.writeHead(400); return res.end("bad path");
      }
      let st;
      try { st = statSync(abs); } catch { st = null; }
      if (!st || !st.isFile()) {
        res.writeHead(404, { "content-type": "text/html; charset=utf-8" });
        return res.end(PAGE("404", `<h1>404</h1><p>Não encontrado: <code>${escapeHtml(relPath)}</code></p>`));
      }
      if (mode === "view" && abs.endsWith(".md")) {
        res.writeHead(200, { "content-type": "text/html; charset=utf-8" });
        return res.end(renderMarkdown(abs, relative(ROOT, abs).split(sep).join("/")));
      }
      res.writeHead(200);
      return res.end(readFileSync(abs));
    }
    res.writeHead(404, { "content-type": "text/html; charset=utf-8" });
    res.end(PAGE("404", "<h1>404</h1>"));
  } catch (err) {
    res.writeHead(500, { "content-type": "text/plain" });
    res.end("server error: " + err.message);
  }
});

server.listen(PORT, HOST, () => {
  console.log(`Vault preview server running at http://${HOST}:${PORT}  (root: ${ROOT})`);
});
