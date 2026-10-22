// Pinned, project-local CLI launcher. No global installation or upgrade.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { spawn } from 'node:child_process';
import './preserve-files.mjs';

const here = path.dirname(fileURLToPath(import.meta.url));
const version = '0.8.139';
const args = process.argv.slice(2);
const config = path.join(here, '..', 'project.json');
if (args[0] === 'render') {
  let output;
  for (let i=1;i<args.length;i++) {
    if (args[i] === '--output' || args[i] === '-o') output=args[i+1];
    if (args[i].startsWith('--output=')) output=args[i].slice(9);
  }
  if (output && fs.existsSync(path.resolve(output))) throw new Error('Output exists; choose a new render version');
  const storyboard=path.join(here,'..','storyboard.json');
  if (fs.existsSync(storyboard) && JSON.parse(fs.readFileSync(storyboard,'utf8')).missing?.length) {
    throw new Error('Resolve the missing screen inserts in plan.md before rendering');
  }
}
if (args[0] === 'render' && !args.some(x => x === '--fps' || x.startsWith('--fps=') || x === '-f')) {
  if (fs.existsSync(config)) args.push('--fps', String(JSON.parse(fs.readFileSync(config, 'utf8')).fps));
}
const preload = pathToFileURL(path.join(here, 'preserve-files.mjs')).href;
process.env.NODE_OPTIONS = ((process.env.NODE_OPTIONS || '') + ' --import=' + preload).trim();
// Optional test/air-gapped entry. The caller supplies an installed CLI; no path is bundled.
if (process.env.YT_EDIT_HYPERFRAMES_ENTRY) {
  const entry = path.resolve(process.env.YT_EDIT_HYPERFRAMES_ENTRY);
  const metadata = JSON.parse(fs.readFileSync(path.join(path.dirname(entry), '..', 'package.json'), 'utf8'));
  if (metadata.version !== version) throw new Error('Expected hyperframes@' + version);
  process.argv = [process.argv[0], entry, ...args];
  await import(pathToFileURL(entry).href);
} else {
  const child = spawn(process.platform === 'win32' ? 'npx.cmd' : 'npx', ['--yes', 'hyperframes@' + version, ...args], {stdio:'inherit',env:process.env});
  child.on('error', error => { process.stderr.write(error.message + '\n'); process.exitCode=1; });
  child.on('exit', code => { process.exitCode = code ?? 1; });
}
