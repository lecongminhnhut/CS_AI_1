import assert from 'node:assert/strict';
import { nextLevel, adjacentLevel } from '../web/progression.js';

const levels = [{id:'first'}, {id:'last'}];
assert.equal(nextLevel(levels,'first'),levels[1]);
assert.equal(nextLevel(levels,'last'),undefined);
assert.equal(nextLevel(levels,'missing'),undefined);
assert.equal(nextLevel([],'first'),undefined);
assert.equal(adjacentLevel(levels,'last',-1),levels[0]);
assert.equal(adjacentLevel(levels,'first',-1),undefined);
assert.equal(adjacentLevel(levels,'last',1),undefined);
assert.equal(adjacentLevel(levels,'missing',-1),undefined);
console.log('Level progression checks passed.');
