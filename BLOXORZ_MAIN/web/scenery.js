import * as THREE from './vendor/three.module.js';

const stone = [0x345969,0x416979,0x527887,0x638a95];
const leaf = [0x287c78,0x358e83,0x50a28e,0x74b79c];

function random(seed) {
  return () => {
    seed = (Math.imul(seed,1664525)+1013904223) >>> 0;
    return seed/4294967296;
  };
}

function part(parent, geometry, color, x=0, y=0, z=0) {
  const model = new THREE.Mesh(geometry,new THREE.MeshStandardMaterial({color,roughness:.92}));
  model.position.set(x,y,z);
  parent.add(model);
  return model;
}

// Bake the static island pieces into one draw call, preserving their normals and colors.
function bakeIsland(group) {
  group.updateMatrixWorld(true);
  const positions=[], normals=[], colors=[];
  const inverse = group.matrixWorld.clone().invert();
  group.traverse(object => {
    if (!object.isMesh) return;
    const geometry = object.geometry.index ? object.geometry.toNonIndexed() : object.geometry.clone();
    geometry.applyMatrix4(new THREE.Matrix4().multiplyMatrices(inverse,object.matrixWorld));
    const p=geometry.attributes.position,n=geometry.attributes.normal,c=geometry.attributes.color;
    const tint = object.material.color;
    for(let i=0;i<p.count;i++) {
      positions.push(p.getX(i),p.getY(i),p.getZ(i));
      normals.push(n.getX(i),n.getY(i),n.getZ(i));
      colors.push(tint.r*(c?c.getX(i):1),tint.g*(c?c.getY(i):1),tint.b*(c?c.getZ(i):1));
    }
    geometry.dispose();
    object.geometry.dispose();
    object.material.dispose();
  });
  group.clear();
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));
  geometry.setAttribute('normal',new THREE.Float32BufferAttribute(normals,3));
  geometry.setAttribute('color',new THREE.Float32BufferAttribute(colors,3));
  const model = new THREE.Mesh(geometry,new THREE.MeshStandardMaterial({vertexColors:true,roughness:.95}));
  model.castShadow = model.receiveShadow = true;
  group.add(model);
}

export function createIslandGeometry(rng, radius) {
  const sides=16,outline=[];
  for(let i=0;i<sides;i++) {
    const a=i*Math.PI*2/sides,r=radius*(.88+rng()*.16);
    outline.push([Math.cos(a)*r,Math.sin(a)*r]);
  }
  const rings = [[1,0],[1.015,-.12],[.94,-.24],[.83,-.58],[.50,-.88]];
  // Generate each ring once so both adjoining faces use exactly the same vertices.
  const vertices=rings.map(([scale,y],ring)=>outline.map(([x,z])=>
    [x*scale,y-(ring>2?rng()*.07:0),z*scale]));
  const positions=[],colors=[],tint=new THREE.Color();
  function triangle(vertices,color) {
    tint.setHex(color);
    for(const v of vertices) {positions.push(...v);colors.push(tint.r,tint.g,tint.b);}
  }
  for(let i=0;i<sides;i++) {
    const next=(i+1)%sides;
    triangle([[0,.018,0],vertices[0][next],vertices[0][i]],i%3?0x57ad99:0x65b6a1);
    rings.slice(1).forEach((_,j) => {
      const aa=vertices[j][i],bb=vertices[j][next];
      const cc=vertices[j+1][i],dd=vertices[j+1][next];
      const color=j===0?0x377f77:stone[(i+j)%stone.length];
      triangle([aa,bb,cc],color);triangle([bb,dd,cc],color);
    });
    // Close the underside with outward-facing triangles, including the final ring seam.
    triangle([[0,-.98,0],vertices.at(-1)[i],vertices.at(-1)[next]],stone[0]);
  }
  const geometry=new THREE.BufferGeometry();
  geometry.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));
  geometry.setAttribute('color',new THREE.Float32BufferAttribute(colors,3));
  geometry.computeVertexNormals();
  return geometry;
}

function branch(parent,a,b,thickness,color=0x655c50) {
  const start=new THREE.Vector3(...a),end=new THREE.Vector3(...b);
  const direction=end.clone().sub(start);
  const model=part(parent,new THREE.CylinderGeometry(thickness*.65,thickness,direction.length(),7),color);
  model.position.copy(start.add(end).multiplyScalar(.5));
  model.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),direction.normalize());
}

function tree(parent,x,z,scale,rng) {
  const tree=new THREE.Group();
  tree.position.set(x,.01,z);
  tree.scale.setScalar(scale);
  parent.add(tree);
  branch(tree,[0,0,0],[.05,.95,-.02],.075);
  const crowns=[[-.28,.85,.04],[.27,.92,-.06],[.03,1.17,.02],[-.06,.91,-.27],[.08,.83,.28]];
  crowns.forEach(([cx,cy,cz],i) => {
    branch(tree,[.02,.40,0],[cx,cy,cz],.035);
    const foliage=new THREE.IcosahedronGeometry(.35,2);
    const points=foliage.attributes.position,phase=rng()*6;
    for(let v=0;v<points.count;v++) {
      const px=points.getX(v),py=points.getY(v),pz=points.getZ(v);
      const irregularity=1+.08*Math.sin(px*17+py*13+phase)*Math.cos(pz*19+phase);
      points.setXYZ(v,px*irregularity,py*irregularity,pz*irregularity);
    }
    const canopy=part(tree,foliage,leaf[i%leaf.length],cx,cy,cz);
    canopy.scale.set(1+rng()*.15,.88+rng()*.18,.9+rng()*.2);
    canopy.rotation.set(rng()*.3,rng()*Math.PI,rng()*.2);
  });
  for(let i=0;i<4;i++) {
    const a=i*Math.PI/2+.2;
    branch(tree,[0,.12,0],[Math.cos(a)*.15,.015,Math.sin(a)*.15],.025);
  }
}

function boulder(parent,x,z,scale,rng) {
  const model=part(parent,new THREE.DodecahedronGeometry(.22,1),stone[Math.floor(rng()*stone.length)],x,.09,z);
  model.scale.set(scale*1.4,scale*.7,scale);
  model.rotation.set(.12,rng()*Math.PI,.12);
}

function flowers(parent,x,z,color) {
  for(let i=0;i<3;i++) {
    const px=x+(i-1)*.07,pz=z+Math.sin(i*2)*.06;
    branch(parent,[px,0,pz],[px,.12+i*.02,pz],.009,0x3d8871);
    part(parent,new THREE.IcosahedronGeometry(.035,1),color,px,.13+i*.02,pz);
  }
}

function ruin(parent,x,z) {
  const tower=new THREE.Group();
  tower.position.set(x,.01,z);parent.add(tower);
  part(tower,new THREE.CylinderGeometry(.19,.24,.12,10),0x889f9f,0,.06,0);
  part(tower,new THREE.CylinderGeometry(.17,.20,.40,10),0xd3d8c5,0,.32,0);
  part(tower,new THREE.CylinderGeometry(.22,.19,.075,10),0x9cae9f,0,.55,0);
  for(let i=0;i<5;i++) {
    const a=i*Math.PI*2/5;
    part(tower,new THREE.BoxGeometry(.075,.11,.075),0xd3d8c5,Math.cos(a)*.16,.63,Math.sin(a)*.16);
  }
  part(tower,new THREE.BoxGeometry(.06,.15,.015),0x416876,0,.35,.191);
  part(tower,new THREE.IcosahedronGeometry(.07,1),0x68a88c,.18,.13,.13);
}

function waterfall(parent) {
  const positions=[];
  for(let i=0;i<10;i++) {
    const y=-i*.17,z=.80+i*.018,x=Math.sin(i*.45)*.014;
    positions.push(x-.10,y,z,x+.10,y,z,x-.10,y-.17,z+.018,
      x+.10,y,z,x+.10,y-.17,z+.018,x-.10,y-.17,z+.018);
  }
  const geometry=new THREE.BufferGeometry();
  geometry.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));
  geometry.computeVertexNormals();
  const water=new THREE.Mesh(geometry,new THREE.MeshStandardMaterial({color:0x98e1dc,emissive:0x347a85,
    emissiveIntensity:.2,transparent:true,opacity:.76,roughness:.35,side:THREE.DoubleSide,depthWrite:false}));
  parent.add(water);
  for(const x of [-.07,.025]) {
    const line=part(parent,new THREE.CylinderGeometry(.008,.014,1.40,5),0xd7f5e6,x,-.70,.88);
    line.rotation.x=-.11;line.castShadow=false;
  }
}

function ridge(parent,center,width,rows,far) {
  const columns=40,positions=[],colors=[],tint=new THREE.Color();
  const low=new THREE.Color(far?0xb2d4d1:0x7aaeb3),high=new THREE.Color(far?0xd2e1d6:0xa6c9c6);
  const vertex=(i,j) => {
    const x=center+(i/columns-.5)*width;
    const ridge=1.1+2.8*Math.exp(-Math.pow((i/columns-.3)*7,2))+
      2*Math.exp(-Math.pow((i/columns-.68)*8,2))+.30*Math.sin(i*.8+j*.7);
    // Continue the foreground slope below the viewport, avoiding a cut-off strip behind the board.
    const fade=Math.sin(Math.PI*j/rows)*Math.sqrt(Math.max(0,Math.sin(Math.PI*i/columns)));
    return j===0 ? [x,-18,9,0] :
      [x,-7.6+ridge*1.2*Math.sin(Math.PI*j/rows),-2.3-j*1.25-(far?4:0),fade];
  };
  for(let j=0;j<rows;j++) for(let i=0;i<columns;i++) {
    const a=vertex(i,j),b=vertex(i+1,j),c=vertex(i,j+1),d=vertex(i+1,j+1);
    for(const v of [a,b,c,b,d,c]) {
      positions.push(v[0],v[1],v[2]);
      tint.copy(low).lerp(high,Math.max(0,Math.min(1,(v[1]+7.6)/4.8)));
      colors.push(tint.r,tint.g,tint.b,v[3]);
    }
  }
  const geometry=new THREE.BufferGeometry();
  geometry.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));
  geometry.setAttribute('color',new THREE.Float32BufferAttribute(colors,4));
  geometry.computeVertexNormals();
  const model=new THREE.Mesh(geometry,new THREE.MeshStandardMaterial({vertexColors:true,roughness:1,
    side:THREE.DoubleSide,transparent:true,opacity:.65,depthWrite:false}));
  model.name='distant-ridge';parent.add(model);
}

export function buildScenery(parent,game) {
  const w=game.rows[0].length,h=game.rows.length;
  const sites=[[-3.0,h*.3-.8,.9],[w+2.1,h*.62-.15,.9],
    [w*.1+.4,h+2.0,.85],[w*.7-.4,-3.7,.85]];
  sites.forEach(([x,z,scale],i) => {
    const rng=random(410+i*79),island=new THREE.Group();
    island.name='garden-island';island.position.set(x,-1.25,z);island.scale.setScalar(scale);
    parent.add(island);
    const surface=part(island,createIslandGeometry(rng,.95),0xffffff);
    surface.material.vertexColors=true;
    tree(island,-.25,-.12,.82,rng);
    if(i!==3) tree(island,.37,-.28,.50,rng);
    else ruin(island,.40,.20);
    boulder(island,-.42,.40,.8,rng);boulder(island,.37,.40,.45,rng);
    flowers(island,.12,.43,i%2?0xe4b7d0:0xf2d799);
    flowers(island,-.57,-.18,0xc9d5ed);
    bakeIsland(island);
    if(i===0 || i===2) waterfall(island);
  });
  ridge(parent,(w-1)/2,Math.max(25,w*2.5)*1.12,6,true);
  ridge(parent,(w-1)/2,Math.max(22,w*2.2)*1.12,6,false);
  const mist=new THREE.Mesh(new THREE.PlaneGeometry(Math.max(42,w*3),Math.max(36,h*3)),
    new THREE.MeshBasicMaterial({color:0xd9e9e2,transparent:true,opacity:.16,depthWrite:false}));
  mist.name='valley-mist';mist.rotation.x=-Math.PI/2;mist.position.set(w/2,-2.4,h/2);
  parent.add(mist);
}
