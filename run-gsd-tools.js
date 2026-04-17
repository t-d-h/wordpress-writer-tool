#!/usr/bin/env node
const { spawn } = require('child_process');
const path = require('path');

const toolPath = path.join(__dirname, '.config', 'kilo', 'get-shit-done', 'bin', 'gsd-tools.cjs');

const args = process.argv.slice(2);
const cmdArgs = [toolPath, ...args];

const child = spawn('node', cmdArgs, {
  stdio: 'inherit',
  env: { ...process.env }
});

child.on('exit', (code) => {
  process.exit(code);
});