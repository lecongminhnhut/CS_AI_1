import assert from 'node:assert/strict';
import * as THREE from '../web/vendor/three.module.js';
import { buildScenery, createIslandGeometry } from '../web/scenery.js';
import { blockGeometry } from '../web/art.js';

for(const dimensions of [[.94,1.98,.94],[1.94,.98,.94],[.94,.98,1.94],[.94,.98,.94]]) {
  const geometry=blockGeometry(...dimensions);
  geometry.computeBoundingBox();
  const actual=geometry.boundingBox.getSize(new THREE.Vector3()).toArray();
  actual.forEach((size,axis)=>assert.ok(Math.abs(size-dimensions[axis])<1e-6,'Beveled blocks retain their roll dimensions'));
  assert.ok([...geometry.attributes.normal.array].every(Number.isFinite));
}

// A closed island shell has exactly two oppositely directed faces at every edge.
for(const seed of [1,410,489,568,647]) {
  let sample=seed;
  const geometry=createIslandGeometry(()=>{
    const value=Math.sin(sample++*12.9898)*43758.5453;
    return value-Math.floor(value);
  },.95);
  const positions=geometry.attributes.position,edges=new Map();
  const key=i=>[positions.getX(i),positions.getY(i),positions.getZ(i)]
    .map(value=>Math.round(value*1e6)).join(',');
  for(let i=0;i<positions.count;i+=3) {
    const triangle=[key(i),key(i+1),key(i+2)];
    assert.equal(new Set(triangle).size,3,'No collapsed faces in the island shell');
    for(let side=0;side<3;side++) {
      const a=triangle[side],b=triangle[(side+1)%3],id=[a,b].sort().join('|');
      const edge=edges.get(id) ?? {count:0,direction:0};
      edge.count++;edge.direction+=a<b?1:-1;edges.set(id,edge);
    }
  }
  for(const edge of edges.values()) {
    assert.equal(edge.count,2,'Island shell must have no open edges or overlapping faces');
    assert.equal(edge.direction,0,'Adjacent faces must share consistent winding');
  }
  geometry.dispose();
}

// Decorative geometry must stay out of the walkable rectangle on all board sizes.
for(const [width,height] of [[1,1],[10,6],[24,16]]) {
  const game={rows:Array(height).fill('.'.repeat(width))};
  const scene=new THREE.Group();
  buildScenery(scene,game);
  scene.updateMatrixWorld(true);
  let meshes=0,triangles=0;
  scene.traverse(object => {
    if(!object.isMesh) return;
    meshes++;
    const geometry=object.geometry;
    triangles+=(geometry.index?.count ?? geometry.attributes.position.count)/3;
    for(const name of ['position','normal']) {
      assert.ok([...geometry.attributes[name].array].every(Number.isFinite),`${name} must be finite`);
    }
    assert.notEqual(geometry.type,'ConeGeometry','Scenery uses shaped foliage and ridges');
  });
  assert.ok(meshes<24,'Static island details should be batched');
  assert.ok(triangles<50000,'Scenery triangle budget');
  for(const island of scene.children.filter(object=>object.name==='garden-island')) {
    const bounds=new THREE.Box3().setFromObject(island);
    const overlaps=bounds.max.x>-.5 && bounds.min.x<width-.5 &&
      bounds.max.z>-.5 && bounds.min.z<height-.5;
    assert.equal(overlaps,false,'Decorative islands must not cover board cells');
    const gapX=Math.max(-.5-bounds.max.x,bounds.min.x-(width-.5),0);
    const gapZ=Math.max(-.5-bounds.max.z,bounds.min.z-(height-.5),0);
    assert.ok(Math.hypot(gapX,gapZ)>=1.25,'Decorative islands need a visible gap from the board');
  }
  for(const ridge of scene.children.filter(object=>object.name==='distant-ridge')) {
    assert.ok(new THREE.Box3().setFromObject(ridge).max.y<-.5,'Ridges stay below the playable platform');
  }
  const again=new THREE.Group();
  buildScenery(again,game);
  assert.deepEqual(again.children[0].children[0].geometry.attributes.position.array,
    scene.children[0].children[0].geometry.attributes.position.array,'Reset must preserve scenery');
}
console.log('Scenery: finite geometry, clear board cells, deterministic details and render budget passed.');
