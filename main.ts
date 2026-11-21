// Entry runner for the Saturday 21 November 2026 front page.
//
// The judged picture already exists in this repository as entry.png, painted
// by paint_front.py. This runner's only job is to hand that exact file to
// the grader: it copies entry.png into the output directory the harness
// points at (MAKEFUN_OUTPUT_DIR, falling back to /output), byte for byte.
// Because the copy never changes a byte, running this file twice always
// produces the same output file.

import { copyFileSync, mkdirSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const repoRoot = dirname(fileURLToPath(import.meta.url));
const source = join(repoRoot, "entry.png");
const destinationDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const destination = join(destinationDir, "entry.png");

mkdirSync(destinationDir, { recursive: true });
copyFileSync(source, destination);

const bytes = statSync(destination).size;
console.log(`copied entry.png to ${destination} (${bytes} bytes)`);
