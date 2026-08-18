#!/usr/bin/env node
/*
 * Convierte en lote los .adoc ya preprocesados (includes y atributos resueltos
 * por scripts/build_docs.py) a Markdown usando downdoc.
 *
 * Uso: node scripts/convert.js <dir-entrada> <dir-salida>
 */
const fs = require('fs')
const path = require('path')

let downdoc
try {
  downdoc = require('downdoc')
} catch (e) {
  console.error('Falta downdoc. Ejecuta: npm --prefix scripts install downdoc')
  process.exit(2)
}

const [inDir, outDir] = process.argv.slice(2)
if (!inDir || !outDir) {
  console.error('Uso: node scripts/convert.js <dir-entrada> <dir-salida>')
  process.exit(2)
}
fs.mkdirSync(outDir, { recursive: true })

let ok = 0
let fail = 0
for (const f of fs.readdirSync(inDir).filter((f) => f.endsWith('.adoc'))) {
  const src = fs.readFileSync(path.join(inDir, f), 'utf8')
  try {
    const md = downdoc(src)
    fs.writeFileSync(path.join(outDir, f.replace(/\.adoc$/, '.md')), md)
    ok++
  } catch (e) {
    console.error(`ERROR convirtiendo ${f}: ${e.message}`)
    fail++
  }
}
console.log(`convert.js: ${ok} convertidos, ${fail} fallidos`)
process.exit(fail ? 1 : 0)
