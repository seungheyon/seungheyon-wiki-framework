#!/usr/bin/env node
// Regenerates reference/graph.html from the current state of the vault's
// markdown files (frontmatter `type`/`domain` + [[wikilinks]]). Run this
// (or double-click open-graph.bat) any time you want an up-to-date graph.

import { readFileSync, writeFileSync, readdirSync, statSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");
const VAULT_NAME = path.basename(ROOT);

const EXCLUDED_DIRS = new Set([".git", ".obsidian", ".idea", ".claude", "node_modules", "scripts"]);

function walk(dir, out = []) {
  for (const entry of readdirSync(dir)) {
    if (EXCLUDED_DIRS.has(entry)) continue;
    const full = path.join(dir, entry);
    const st = statSync(full);
    if (st.isDirectory()) walk(full, out);
    else if (entry.endsWith(".md")) out.push(full);
  }
  return out;
}

function toPosix(p) {
  return p.split(path.sep).join("/");
}

function parseFrontmatter(text) {
  const fm = { type: null, domain: null };
  if (!text.startsWith("---")) return fm;
  const end = text.indexOf("\n---", 3);
  if (end === -1) return fm;
  const block = text.slice(3, end);
  for (const line of block.split("\n")) {
    const m = /^(type|domain)\s*:\s*(.+?)\s*$/.exec(line);
    if (m) fm[m[1]] = m[2].replace(/^["']|["']$/g, "");
  }
  return fm;
}

function firstHeading(text) {
  const m = /^#\s+(.+)$/m.exec(text);
  return m ? m[1].trim() : null;
}

function extractLinks(text) {
  const links = [];
  const re = /\[\[([^\]|#]+)(?:[^\]]*)?\]\]/g;
  let m;
  while ((m = re.exec(text))) {
    const target = m[1].trim();
    if (target) links.push(target);
  }
  return links;
}

const files = walk(ROOT);

const nodes = new Map(); // id -> node
const byBasename = new Map(); // lowercased basename (no ext) -> [ids]

for (const full of files) {
  const relPath = toPosix(path.relative(ROOT, full));
  const id = relPath.replace(/\.md$/i, "");
  const text = readFileSync(full, "utf8");
  const fm = parseFrontmatter(text);
  const inRaw = /(^|\/)raw\//.test(relPath);
  const type = inRaw ? "raw" : fm.type || "other";
  const domain = fm.domain || relPath.split("/")[0];
  const title = firstHeading(text) || path.basename(id);

  nodes.set(id.toLowerCase(), {
    id,
    key: id.toLowerCase(),
    title,
    type,
    domain,
    path: relPath,
    links: extractLinks(text),
    degree: 0,
  });

  const base = path.basename(id).toLowerCase();
  if (!byBasename.has(base)) byBasename.set(base, []);
  byBasename.get(base).push(id.toLowerCase());
}

function resolveTarget(rawTarget, sourceId) {
  const target = rawTarget.trim().replace(/\\/g, "/").replace(/^\.\//, "");
  const sourceDir = path.posix.dirname(sourceId);
  const joined = target.startsWith("/")
    ? target.slice(1)
    : path.posix.normalize(path.posix.join(sourceDir, target));
  const key = joined.toLowerCase();
  if (nodes.has(key)) return key;

  const base = path.posix.basename(target).toLowerCase();
  const candidates = byBasename.get(base);
  if (candidates && candidates.length > 0) return candidates[0];

  return null; // unresolved -> synthetic "missing" node
}

const edgeSet = new Set();
const edges = [];
const missingNodes = new Map();

for (const node of nodes.values()) {
  for (const rawTarget of node.links) {
    const resolved = resolveTarget(rawTarget, node.id);
    let targetKey;
    if (resolved) {
      targetKey = resolved;
    } else {
      const label = rawTarget.split("/").pop();
      const missingKey = "missing:" + label.toLowerCase();
      targetKey = missingKey;
      if (!missingNodes.has(missingKey)) {
        missingNodes.set(missingKey, {
          id: missingKey,
          key: missingKey,
          title: label,
          type: "missing",
          domain: node.domain,
          path: null,
          links: [],
          degree: 0,
        });
      }
    }
    if (targetKey === node.key) continue;
    const edgeKey = node.key + "->" + targetKey;
    if (edgeSet.has(edgeKey)) continue;
    edgeSet.add(edgeKey);
    edges.push({ source: node.key, target: targetKey });
  }
}

for (const [k, v] of missingNodes) nodes.set(k, v);
for (const e of edges) {
  nodes.get(e.source).degree++;
  nodes.get(e.target).degree++;
}

const graphNodes = [...nodes.values()].map(({ links, ...rest }) => rest);

const graphData = {
  generatedAt: new Date().toISOString(),
  vaultName: VAULT_NAME,
  nodes: graphNodes,
  edges,
};

const templatePath = path.join(__dirname, "graph-template.html");
const template = readFileSync(templatePath, "utf8");
const html = template.replace(
  "/*__GRAPH_DATA__*/",
  JSON.stringify(graphData)
);

const outPath = path.join(ROOT, "reference", "graph.html");
writeFileSync(outPath, html, "utf8");

console.log(
  `graph.html generated: ${graphNodes.length} nodes, ${edges.length} edges -> ${toPosix(
    path.relative(ROOT, outPath)
  )}`
);
