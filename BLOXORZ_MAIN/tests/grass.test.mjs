import assert from 'node:assert/strict';
import * as THREE from '../web/vendor/three.module.js';
import { buildTiles } from '../web/art.js';

const game={level:'grass-check',rows:['SohxFGB.........',...Array(15).fill('.'.repeat(16))],
  status:'playing',bridge_cells:[[[0,6],'gate']],state:{bridges:['gate']}};
function samples(level=game.level) {
  const stage=new THREE.Group(),tiles=new Map();
  buildTiles(stage,{...game,level},tiles);
  return new Map([...tiles].flatMap(([key,item])=>{
    const grass=item.model.getObjectByName('ground-grass');
    if('SohxFGB'.includes(item.tile)) assert.equal(grass,undefined,'Special tiles stay clear');
    return grass?[[key,grass]]:[];
  }));
}
const first=samples(),again=samples(),kinds=new Set();
assert.ok(first.size>256*.20 && first.size<256*.50,'Grass should be sparse, with clear floor between patches');
assert.deepEqual([...again.keys()],[...first.keys()],'Grass positions stay stable after moving');
for(const [key,grass] of first) {
  kinds.add(grass.userData.kind);
  const bounds=new THREE.Box3().setFromObject(grass);
  assert.ok(bounds.min.y>=0 && bounds.max.y<=.085,'Grass stays short and above the floor');
  assert.ok(bounds.min.x>-.46 && bounds.max.x<.46 && bounds.min.z>-.46 && bounds.max.z<.46,'Grass stays inside its tile');
  assert.ok([...grass.geometry.attributes.position.array].every(Number.isFinite));
  assert.deepEqual(grass.geometry.attributes.position.array,again.get(key).geometry.attributes.position.array,
    'Grass must not flicker or change shape when the board rebuilds');
  assert.deepEqual(grass.geometry.attributes.color.array,again.get(key).geometry.attributes.color.array,
    'Grass colors stay stable after moving');
}
assert.equal(kinds.size,6,'All six grass varieties are represented');
assert.notDeepEqual([...samples('another-level').keys()],[...first.keys()],
  'Different levels should have different grass distributions');
console.log('Grass: six varieties, low height, irregular placement, clear special tiles and stable rebuilds passed.');
