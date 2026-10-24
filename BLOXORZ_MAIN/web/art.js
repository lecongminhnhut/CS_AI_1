import * as THREE from './vendor/three.module.js';
import { bridgeHinge } from './motion.js';

export const palette = { grass: 0x2baf9e, rock: 0x244f68, coral: 0xc85f59, cream: 0xf2eee0, block: 0xc4aff2, inactiveBlock: 0x9c86c9 };

export function blockGeometry(w,h,d) {
  const geometry=new THREE.BoxGeometry(w,h,d,4,4,4);
  const positions=geometry.attributes.position,normals=geometry.attributes.normal;
  const radius=.018,half=[w/2,h/2,d/2],point=new THREE.Vector3(),inner=new THREE.Vector3();
  const remap=(value,extent) => Math.abs(value)<1e-6?0:
    Math.sign(value)*(Math.abs(value)>extent*.75?extent:extent-radius);
  for(let i=0;i<positions.count;i++) {
    point.set(remap(positions.getX(i),half[0]),remap(positions.getY(i),half[1]),remap(positions.getZ(i),half[2]));
    inner.set(...point.toArray().map((value,axis)=>THREE.MathUtils.clamp(value,-half[axis]+radius,half[axis]-radius)));
    const normal=point.clone().sub(inner).normalize();
    point.copy(inner).addScaledVector(normal,radius);
    positions.setXYZ(i,point.x,point.y,point.z);
    normals.setXYZ(i,normal.x,normal.y,normal.z);
  }
  return geometry;
}

export function mesh(parent, geometry, color, x = 0, y = 0, z = 0) {
  const object = new THREE.Mesh(geometry, new THREE.MeshStandardMaterial({color, roughness:.9, flatShading:true}));
  object.position.set(x, y, z);
  object.castShadow = true;
  object.receiveShadow = true;
  parent.add(object);
  return object;
}

export function buildGoalFlag(parent) {
  const flag = new THREE.Group();
  parent.add(flag);
  mesh(flag,new THREE.CylinderGeometry(.13,.17,.08,8),palette.cream,0,.04,0);
  mesh(flag,new THREE.CylinderGeometry(.025,.035,1.7,8),palette.cream,0,.9,0);
  mesh(flag,new THREE.SphereGeometry(.06,8,6),0xf3ce82,0,1.78,0);
  const shape = new THREE.Shape();
  shape.moveTo(.03,1.66);
  shape.lineTo(.68,1.66);
  shape.lineTo(.53,1.46);
  shape.lineTo(.68,1.26);
  shape.lineTo(.03,1.26);
  shape.closePath();
  const cloth = mesh(flag,new THREE.ShapeGeometry(shape),palette.coral);
  cloth.material.side = THREE.DoubleSide;
  return flag;
}

export function buildFireworks(parent, [r,c]) {
  const colors = [0xffce79,0xf59fbb,0xc4aff2,0x9cebd8,0xffe9b5];
  const bursts = colors.map((color,b) => {
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position',new THREE.Float32BufferAttribute(new Float32Array(48*6),3));
    const sparks = new THREE.LineSegments(geometry,new THREE.LineBasicMaterial({
      color,transparent:true,depthWrite:false,toneMapped:false
    }));
    sparks.position.set(c+Math.sin(b*2.4)*.8,1.9+(b%2)*.6,r+Math.cos(b*2.4)*.6);
    sparks.frustumCulled = false;
    parent.add(sparks);
    return sparks;
  });
  return elapsed => {
    bursts.forEach((sparks,b) => {
      const age = elapsed-b*.45;
      sparks.visible = age >= 0 && age < 1.6 && elapsed < 3.4;
      if (!sparks.visible) return;
      sparks.material.opacity = 1-age/1.6;
      const positions = sparks.geometry.attributes.position;
      for (let i=0;i<48;i++) {
        const y = 1-2*(i+.5)/48, radial = Math.sqrt(1-y*y), angle = i*2.39996;
        for (let end=0;end<2;end++) {
          const t = Math.max(0,age-end*.09), distance = 2.1*t;
          positions.setXYZ(i*2+end,Math.cos(angle)*radial*distance,
            y*distance-.8*t*t,Math.sin(angle)*radial*distance);
        }
      }
      positions.needsUpdate = true;
    });
    return elapsed < 3.4;
  };
}

function box(parent, w, h, d, color, x = 0, y = 0, z = 0) {
  return mesh(parent, new THREE.BoxGeometry(w, h, d), color, x, y, z);
}

function rock(parent, depth, seed, radius = .5, sides = [0,1,2,3]) {
  if (!sides.length) return;
  const points = [], colors = [];
  const corners = [[-radius,-radius],[radius,-radius],[radius,radius],[-radius,radius]];
  const color = new THREE.Color();
  for (const side of sides) {
    const a = corners[side], b = corners[(side + 1) % 4];
    const inset = .97;
    const bottom = -depth;
    const vertices = [[...a], [...b], [b[0]*inset,b[1]*inset], [...a], [b[0]*inset,b[1]*inset], [a[0]*inset,a[1]*inset]];
    vertices.forEach(([x,z], i) => {
      points.push(x, i === 2 || i === 4 || i === 5 ? bottom : -.12, z);
      color.setHex(side % 2 ? 0x31566c : 0x29465f).multiplyScalar(1 + (seed % 3) * .035);
      colors.push(color.r, color.g, color.b);
    });
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position',new THREE.Float32BufferAttribute(points,3));
  geometry.setAttribute('color',new THREE.Float32BufferAttribute(colors,3));
  geometry.computeVertexNormals();
  const object = mesh(parent, geometry, 0xffffff);
  object.material.vertexColors = true;
  return object;
}

function grass(parent, r, c, level) {
  // Seed by level and cell so rebuilding after a move never shuffles the grass.
  let seed=(Math.imul(r+1,73856093)^Math.imul(c+1,19349663))>>>0;
  for(const character of String(level??'')) seed=Math.imul(seed^character.charCodeAt(0),16777619)>>>0;
  seed=Math.imul(seed^(seed>>>16),0x7feb352d);
  seed=Math.imul(seed^(seed>>>15),0x846ca68b)^(seed>>>16);
  const random=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;};
  if(random()>.38) return;
  const kind=Math.floor(random()*6),points=[],colors=[],tint=new THREE.Color();
  const greens=[0x63b78c,0x9acd8b,0x3f9a75,0x82b993,0xb4cd8d,0x4b9f80];
  const shade=.94+random()*.12;
  const triangle=(a,b,c,color)=>{
    tint.setHex(color).multiplyScalar(shade);
    for(const point of [a,b,c]) {points.push(...point);colors.push(tint.r,tint.g,tint.b);}
  };
  const patches=random()<.25?2:1;
  for(let patch=0;patch<patches;patch++) {
    const plant=patch?Math.floor(random()*6):kind,scale=.75+random()*.28;
    const angle=random()*Math.PI*2,radius=.20+random()*.13;
    const x=Math.cos(angle)*radius,z=Math.sin(angle)*radius,rotation=random()*Math.PI*2;
    const local=(u,y,v)=>[x+scale*1.3*(u*Math.cos(rotation)-v*Math.sin(rotation)),y*scale,z+scale*1.3*(u*Math.sin(rotation)+v*Math.cos(rotation))];
    if(plant===1) {
      // Low clover: three small rounded leaves, lifted just above the floor.
      for(let leaf=0;leaf<3;leaf++) {
        const direction=leaf*Math.PI*2/3,dx=Math.cos(direction),dz=Math.sin(direction);
        const center=local(dx*.024,.024,dz*.024);
        for(let segment=0;segment<7;segment++) {
          const rim=t=>local(dx*.024+Math.cos(t)*.023,.019+Math.sin(t)*.003,dz*.024+Math.sin(t)*.023);
          triangle(center,rim(segment*Math.PI*2/7),rim((segment+1)*Math.PI*2/7),greens[leaf]);
        }
      }
    } else if(plant===2) {
      // A small fan of broad leaves; each leaf folds along its raised midrib.
      for(let leaf=0;leaf<3;leaf++) {
        const direction=leaf*2.1,dx=Math.cos(direction),dz=Math.sin(direction),length=.04+random()*.025;
        const base=local(0,.009,0),tip=local(dx*length,.025,dz*length);
        const middle=local(dx*length*.45,.045,dz*length*.45);
        const left=local(dx*length*.45-dz*.014,.018,dz*length*.45+dx*.014);
        const right=local(dx*length*.45+dz*.014,.018,dz*length*.45-dx*.014);
        triangle(base,left,middle,greens[0]);triangle(left,tip,middle,greens[0]);
        triangle(base,middle,right,greens[2]);triangle(middle,tip,right,greens[2]);
      }
    } else if(plant===4) {
      // Small cushions of moss, made of uneven low mounds.
      for(let mound=0;mound<3;mound++) {
        const u=(random()-.5)*.065,v=(random()-.5)*.065,r=.022+random()*.018;
        const center=local(u,.023+random()*.012,v);
        for(let segment=0;segment<8;segment++) {
          const rim=t=>local(u+Math.cos(t)*r,.008,v+Math.sin(t)*r);
          triangle(center,rim(segment*Math.PI/4),rim((segment+1)*Math.PI/4),greens[(segment+mound)%greens.length]);
        }
      }
    } else if(plant===5) {
      // Fine stems with pale seed heads, still below the block's contact surface.
      for(let stem=0;stem<3;stem++) {
        const u=(stem-1)*.025,v=(random()-.5)*.025,height=.05+random()*.02,lean=(random()-.5)*.025;
        triangle(local(u-.004,.008,v),local(u+.004,.008,v),local(u+lean,height,v+.01),greens[2]);
        const center=local(u+lean,height,v+.01);
        for(let petal=0;petal<5;petal++) {
          const rim=t=>local(u+lean+Math.cos(t)*.012,height-.004,v+.01+Math.sin(t)*.012);
          triangle(center,rim(petal*Math.PI*2/5),rim((petal+1)*Math.PI*2/5),0xd6dca6);
        }
      }
    } else {
      // Short upright blades or a flatter, spreading tuft.
      const blades=plant===0?3+Math.floor(random()*3):4+Math.floor(random()*3);
      for(let blade=0;blade<blades;blade++) {
        const direction=random()*Math.PI*2,dx=Math.cos(direction),dz=Math.sin(direction);
        const baseX=(random()-.5)*.045,baseZ=(random()-.5)*.045;
        const height=plant===0?.045+random()*.035:.025+random()*.025;
        const lean=plant===0?.014:.035;
        const baseA=local(baseX-dz*.009,.008,baseZ+dx*.009);
        const baseB=local(baseX+dz*.009,.008,baseZ-dx*.009);
        const middle=local(baseX+dx*lean*.5,height*.65,baseZ+dz*lean*.5);
        const tip=local(baseX+dx*lean,height,baseZ+dz*lean);
        triangle(baseA,baseB,middle,greens[blade%greens.length]);
        triangle(baseB,tip,middle,greens[blade%greens.length]);
      }
    }
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position',new THREE.Float32BufferAttribute(points,3));
  geometry.setAttribute('color',new THREE.Float32BufferAttribute(colors,3));
  geometry.computeVertexNormals();
  const tuft = mesh(parent, geometry, 0xffffff);
  tuft.name='ground-grass';tuft.userData.kind=kind;
  tuft.castShadow=false;
  tuft.material.vertexColors=true;
  tuft.material.side = THREE.DoubleSide;
}

export function buildTiles(stage, game, tileObjects) {
  tileObjects.clear();
  const bridgeGroups = new Map(game.bridge_cells.map(([cell, group]) => [cell.join(','), group]));
  const opened = new Set(game.state.bridges);
  if (game.status === 'lost') for (const change of game.transition?.bridges ?? []) {
    if (change.open) opened.add(change.group); else opened.delete(change.group);
  }
  game.rows.forEach((row,r) => [...row].forEach((tile,c) => {
    if (tile === ' ') return;
    if (game.status === 'lost' && game.transition?.fallen?.some(([fr,fc]) => fr === r && fc === c)) return;
    const group = new THREE.Group();
    group.position.set(c,0,r);
    stage.add(group);
    const model = new THREE.Group();
    group.add(model);
    const item = {group, model, tile, marker:null, bridge:bridgeGroups.get([r,c].join(','))};
    const exposed = [[-1,0],[0,1],[1,0],[0,-1]].flatMap(([dr,dc],side) => {
      const neighbor = game.rows[r+dr]?.[c+dc] ?? ' ';
      return ' BF'.includes(neighbor) ? [side] : [];
    });
    tileObjects.set([r,c].join(','), item);
    if (tile === 'B') {
      const hinge = bridgeHinge(game.rows,r,c);
      item.closedRotation = hinge.rotation;
      model.position.fromArray(hinge.offset);
      const deck = new THREE.Group();
      deck.position.fromArray(hinge.offset).negate();
      model.add(deck);
      for (let i = 0; i < 4; i++) box(deck,.94,.13,.22,0xa6b3a2,0,-.065,-.36+i*.24);
      for (const x of [-.35,.35]) box(deck,.045,.035,.98,0x416c72,x,.012,0);
      const pin = mesh(group,new THREE.CylinderGeometry(.045,.045,.92,8),0x40626a,...hinge.offset);
      pin.rotation.z = hinge.offset[2] ? Math.PI/2 : 0;
      if (!hinge.offset[2]) pin.rotation.x = Math.PI/2;
      if (!opened.has(item.bridge)) model.rotation.set(...hinge.rotation);
      return;
    }
    if (tile === 'G') {
      rock(model, .35, r+c, .5, exposed);
      box(model,.75,.05,.75,0x163d51,0,-.3,0);
      for (const side of [-1,1]) {
        box(model,.17,.35,.99,palette.cream,side*.415,-.16,0);
        box(model,.66,.35,.17,palette.cream,0,-.16,side*.415);
        box(model,.045,.05,.96,palette.coral,side*.47,.025,0);
        box(model,.96,.05,.045,palette.coral,0,.025,side*.47);
      }
      if (game.status === 'won') buildGoalFlag(model);
      return;
    }
    if (tile === 'F') {
      box(model,.97,.17,.97,0xb5816a,0,-.085,0);
      box(model,.91,.035,.91,0xe3af78,0,.006,0);
      const cracks = [
        [[-.45,-.3],[-.26,-.22],[-.15,-.04],[.04,.05],[.12,.24],[.32,.33],[.45,.31]],
        [[-.15,-.04],[-.08,-.22],[.11,-.31],[.17,-.45]],
        [[.04,.05],[.23,-.04],[.31,-.22],[.45,-.26]],
        [[-.15,-.04],[-.32,.08],[-.28,.25],[-.4,.45]],
        [[.12,.24],[.02,.34],[.04,.45]],
        [[-.26,-.22],[-.3,-.37],[-.25,-.45]],
        [[.23,-.04],[.35,.08],[.42,.07]],
        [[-.28,.25],[-.12,.28],[-.06,.23]],
      ];
      const vertices = [];
      cracks.forEach((path, branch) => {
        for (let i = 1; i < path.length; i++) {
          const [ax,az] = path[i-1], [bx,bz] = path[i];
          const width = (branch ? .008 : .015) * (1 - .5 * i / path.length);
          const length = Math.hypot(bx-ax,bz-az);
          const dx = (bz-az)/length*width, dz = (ax-bx)/length*width;
          vertices.push(ax-dx,.025,az-dz,bx-dx,.025,bz-dz,bx+dx,.025,bz+dz,
            ax-dx,.025,az-dz,bx+dx,.025,bz+dz,ax+dx,.025,az+dz);
        }
      });
      const geometry = new THREE.BufferGeometry();
      geometry.setAttribute('position',new THREE.Float32BufferAttribute(vertices,3));
      geometry.computeVertexNormals();
      mesh(model,geometry,0x704936).material.side = THREE.DoubleSide;
      return;
    }
    rock(model, .3, r*13+c, .5, exposed);
    box(model,.995,.10,.995,0x226f78,0,-.13,0);
    const greens = [0x29a99b,0x32b3a1,0x35af9d,0x2ea397];
    box(model,.985,.10,.985,greens[(r*3+c)%greens.length],0,-.05,0);
    if(tile==='.') grass(model,r,c,game.level);
    if ('ohx'.includes(tile)) {
      item.marker = new THREE.Group();
      model.add(item.marker);
      mesh(item.marker,new THREE.CylinderGeometry(.32,.36,.065,8),0x426c80,0,.035,0);
      if (tile === 'o') {
        mesh(item.marker,new THREE.CylinderGeometry(.28,.30,.045,8),0x53c6b4,0,.08,0);
        const ring = mesh(item.marker,new THREE.RingGeometry(.16,.20,32),0xe1fff0,0,.107,0);
        ring.rotation.x = -Math.PI/2;
      } else if (tile === 'h') {
        for (const angle of [-Math.PI/4,Math.PI/4]) {
          const bar = box(item.marker,.075,.055,.43,0xe0c1e0,0,.085,0);
          bar.rotation.y = angle;
        }
      } else {
        for (const start of [Math.PI/2, -Math.PI/2]) {
          const bracket = mesh(item.marker,new THREE.TorusGeometry(.17,.025,6,20,Math.PI),0xf1dca1,start>0?-.05:.05,.085,0);
          bracket.rotation.set(-Math.PI/2,0,start);
        }
      }
    }
    if (tile === 'S') {
      const ring = mesh(model,new THREE.RingGeometry(.14,.165,24),0x9ce0ca,0,.011,0);
      ring.rotation.x = -Math.PI/2;
    }
  }));
}

export { buildScenery } from './scenery.js?v=mountain-scale';
