import fs from "node:fs";
import path from "node:path";

const inputPath = process.env.INPUT_PATH;
const outputPath = process.env.OUTPUT_PATH;

if (!inputPath || !outputPath) {
  throw new Error("Please set INPUT_PATH and OUTPUT_PATH.");
}

if (!fs.existsSync(inputPath)) {
  throw new Error(`Input file not found: ${inputPath}`);
}

const content = fs.readFileSync(inputPath, "utf-8");
const lines = content
  .split("\n")
  .map((line) => line.trim())
  .filter(Boolean);

const data = lines.map((line) => JSON.parse(line));

fs.mkdirSync(path.dirname(outputPath), { recursive: true });
fs.writeFileSync(outputPath, JSON.stringify(data, null, 2));

console.log(`Converted ${lines.length} lines from ${inputPath} -> ${outputPath}`);
