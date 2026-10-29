import assert from 'node:assert/strict';
import {countRolls, replayNextRoll} from '../web/replay.js';

const actions = ['switch', 'left', 'up', 'switch', 'right'];
assert.equal(countRolls(actions), 3);
assert.equal(countRolls(actions, 1), 0);
assert.equal(countRolls(actions, 2), 1);
assert.equal(countRolls(actions, 4), 2);
assert.equal(countRolls([]), 0);

const performed = [];
const move = async action => { performed.push(action); return true; };
let result = await replayNextRoll(actions, 0, move);
assert.deepEqual(result, {index: 2, moved: true});
assert.deepEqual(performed, ['switch', 'left']);
result = await replayNextRoll(actions, result.index, move);
assert.deepEqual(result, {index: 3, moved: true});
result = await replayNextRoll(actions, result.index, move);
assert.deepEqual(result, {index: 5, moved: true});
assert.deepEqual(performed, actions);
assert.deepEqual(await replayNextRoll(actions, 5, move), {index: 5, moved: false});

const failed = [];
result = await replayNextRoll(actions, 0, async action => {
  failed.push(action);
  return action === 'switch';
});
assert.deepEqual(result, {index: 1, moved: false});
assert.deepEqual(failed, ['switch', 'left']);
assert.equal(countRolls(actions, result.index), 0);
assert.deepEqual(await replayNextRoll(['switch'], 0, move), {index: 1, moved: false});
