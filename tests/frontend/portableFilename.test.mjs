import assert from 'node:assert/strict';
import test from 'node:test';
import { portableFilename } from '../../electron/src/main/portable-filename.ts';

test('repairs superscript Windows device aliases without changing ordinary names', () => {
  for (const prefix of ['COM', 'LPT', 'com', 'lpt']) {
    for (const digit of ['\u00b9', '\u00b2', '\u00b3']) {
      for (const suffix of ['', '.wav', '.part.wav']) {
        const name = `${prefix}${digit}${suffix}`;
        assert.equal(portableFilename(name), `_${name}`);
      }
    }
  }
  for (const name of ['COM0.wav', 'COM10.wav', 'LPT4notes.wav', 'voice\u00b2.wav']) {
    assert.equal(portableFilename(name), name);
  }
});
