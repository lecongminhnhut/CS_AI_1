import assert from 'node:assert/strict';
import * as THREE from '../web/vendor/three.module.js';
import { buildGoalFlag, buildFireworks, buildTiles } from '../web/art.js';

const stage = new THREE.Group(), tiles = new Map();
const game = {rows:['G'],bridge_cells:[],state:{bridges:[]},status:'playing'};
buildTiles(stage,game,tiles);
const normalParts = tiles.get('0,0').model.children.length;
stage.clear();
buildTiles(stage,{...game,status:'won'},tiles);
assert.equal(tiles.get('0,0').model.children.length,normalParts+1);
const flag = buildGoalFlag(new THREE.Group());
assert.ok(new THREE.Box3().setFromObject(flag).max.y > 1.7);
assert.ok(new THREE.Box3().setFromObject(flag).min.y >= 0);

const effects = new THREE.Group(), update = buildFireworks(effects,[2,3]);
assert.equal(effects.children.length,5);
update(-.1);
assert.ok(effects.children.every(burst => !burst.visible));
assert.equal(update(.6),true);
const active = effects.children.filter(burst => burst.visible);
assert.equal(active.length,2);
assert.ok(active.every(burst => burst.material.opacity > 0 && burst.material.opacity < 1));
for (const burst of active) {
  const vertices = burst.geometry.attributes.position;
  assert.ok([...vertices.array].every(Number.isFinite));
  assert.ok(new THREE.Vector3().fromBufferAttribute(vertices,0)
    .distanceTo(new THREE.Vector3().fromBufferAttribute(vertices,1)) > 0);
}
assert.equal(update(3.4),false);
assert.ok(effects.children.every(burst => !burst.visible));
console.log('Victory: goal flag only on winning, flag above floor, staggered sparks, trails and effect expiry passed.');
