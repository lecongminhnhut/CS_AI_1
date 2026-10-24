import assert from 'node:assert/strict';
import { fallPlan, createFallMotion, bridgeHinge } from '../web/motion.js';

for (const [cells, support, expected] of [
  [[[0, 1], [0, 2]], [[0, 1]], [1, 0]],
  [[[0, 1], [0, 2]], [[0, 2]], [-1, 0]],
  [[[1, 0], [2, 0]], [[1, 0]], [0, 1]],
  [[[1, 0], [2, 0]], [[2, 0]], [0, -1]],
]) {
  const plan = fallPlan({cells, split:false}, support, 'right');
  assert.equal(plan.mode, 'edge');
  assert.deepEqual(plan.direction, expected);
  const center = [plan.pivot[0], .5, plan.pivot[2]];
  const pose = createFallMotion(plan, center);
  assert.deepEqual(pose(0).position, center);
  assert.ok(pose(.3).angle > 0);
  assert.ok(pose(.3).position[1] < .5);
  assert.ok(pose(1.6).position[1] < -1);
}
const free = createFallMotion(fallPlan({cells:[[0,0]],split:false}, [], 'down'), [0,.5,0]);
assert.equal(free(0).position[1], .5);
assert.ok(Math.abs(free(1).position[1] - (.5 - 9.81 / 2)) < 1e-9);
const cube = fallPlan({cells:[[0,1],[0,4]],split:true}, [[0,4]], 'left');
assert.equal(cube.mode, 'free');
console.log('Fall motion: 4 edge directions, support pivot, free-fall gravity, and split cube passed.');

for (const [rows, offset, rotation] of [
  [[' . ', ' B ', '   '], [0,0,-.5], [Math.PI/2,0,0]],
  [['   ', ' B.', '   '], [.5,0,0], [0,0,Math.PI/2]],
  [['   ', ' B ', ' . '], [0,0,.5], [-Math.PI/2,0,0]],
  [['   ', '.B ', '   '], [-.5,0,0], [0,0,-Math.PI/2]],
]) {
  const hinge = bridgeHinge(rows,1,1);
  assert.deepEqual(hinge.offset,offset);
  hinge.rotation.forEach((value,i) => assert.ok(Math.abs(value-rotation[i])<1e-9));
  const tipY = -hinge.offset[0]*Math.sin(hinge.rotation[2]) + hinge.offset[2]*Math.sin(hinge.rotation[0]);
  assert.ok(tipY < 0, 'Closed bridge folds below the floor');
}
assert.deepEqual(bridgeHinge(['.BBB '],0,2).offset,[-.5,0,0]);
console.log('Bridge hinges: 4 land edges, downward folding, and contiguous bridge spans passed.');
