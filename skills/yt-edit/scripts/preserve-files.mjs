// Keep render intermediates and cache evidence. Manage storage outside this workflow.
import fs from 'node:fs';
import { syncBuiltinESMExports } from 'node:module';
const noop = () => undefined;
const asyncNoop = (...args) => {
  const callback = args.at(-1);
  if (typeof callback === 'function') queueMicrotask(() => callback(null));
};
for (const name of ['rmSync','unlinkSync','rmdirSync']) fs[name] = noop;
for (const name of ['rm','unlink','rmdir']) {
  fs[name] = asyncNoop;
  fs.promises[name] = async () => undefined;
}
syncBuiltinESMExports();
