import * as THREE from './vendor/three.module.js';
import { buildTiles, buildScenery, buildGoalFlag, buildFireworks, blockGeometry, palette } from './art.js?v=ground-fit';
import { fallPlan, createFallMotion } from './motion.js';
import { nextLevel, adjacentLevel } from './progression.js?v=skeleton02';
import { renderTileLegend } from './legend.js?v=wild-grass2';
import { initTestcases } from './testcases.js';

const $ = selector => document.querySelector(selector);
const viewport = $('#viewport');
const tooltip = $('#tile-tooltip');
const tileHelp = {
  o: '○ Công tắc mềm: khối đứng, khối nằm hoặc khối con đều kích hoạt khi đi vào.',
  h: '× Công tắc nặng: chỉ khối nguyên đứng mới kích hoạt.',
  x: '() Ô tách: đứng khối nguyên lên ô để tách thành hai khối 1×1. Click khối hoặc nhấn Space để chọn.',
  F: 'Sàn dễ vỡ: đỡ khối nằm và khối 1×1; vỡ khi khối nguyên đứng lên.',
  B: 'Cầu: công tắc điều khiển đóng/mở. Chỉ đi qua khi cầu đã mở.',
  G: 'Giếng đích: lăn khối nguyên đứng vào đây để hoàn thành màn.'
};
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.localClippingEnabled = true;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
viewport.append(renderer.domElement);
const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0xd8e5df,27,60);
const camera = new THREE.OrthographicCamera(-7, 7, 7, -7, .1, 100);
scene.add(new THREE.HemisphereLight(0xb9e9ed, 0x47626a, 1.8));
const sun = new THREE.DirectionalLight(0xffe4ce, 2.4);
sun.position.set(-5, 13, 8);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
Object.assign(sun.shadow.camera, { left: -16, right: 16, top: 16, bottom: -16, near: 1, far: 40 });
sun.shadow.bias = -.00005;
scene.add(sun, sun.target);
const fill = new THREE.DirectionalLight(0xe6f7f1, 1.0);
fill.position.set(8, 6, -8);
scene.add(fill);
renderTileLegend(scene);
const stage = new THREE.Group();
const pieces = new THREE.Group();
const scenery = new THREE.Group();
const celebration = new THREE.Group();
scene.add(scenery, stage, pieces, celebration);
const tileObjects = new Map();
let sceneryLevel;
let game, busy = false, replaying = false, path = null, animation = null;
let testcasePanel;
let stopRequested = false;
let replayIndex = 0;
let victoryEffects = null;
let yaw = .40, pitch = .83, zoom = .86;
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;

function box(parent, x, y, z, w, h, d, color, emissive = 0) {
  const mesh = new THREE.Mesh(blockGeometry(w,h,d),
    new THREE.MeshStandardMaterial({ color, roughness: .62, metalness: .08, emissive, emissiveIntensity: .2 }));
  mesh.position.set(x, y, z);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  parent.add(mesh);
  return mesh;
}

function clear(group) {
  group.traverse(object => {
    object.geometry?.dispose();
    if (object.material) object.material.dispose();
  });
  group.clear();
}

function cameraPosition() {
  if (!game) return;
  const x = (game.rows[0].length - 1) / 2;
  const z = (game.rows.length - 1) / 2;
  camera.position.set(x + Math.sin(yaw) * 18 * Math.cos(pitch), Math.sin(pitch) * 18,
                      z + Math.cos(yaw) * 18 * Math.cos(pitch));
  camera.lookAt(x, 0, z);
  const aspect = viewport.clientWidth / viewport.clientHeight;
  const span = Math.max(game.rows.length * .85 + 2.4, (game.rows[0].length + 3) / aspect) / 2;
  camera.left = -span * aspect;
  camera.right = span * aspect;
  camera.top = span;
  camera.bottom = -span;
  camera.zoom = zoom;
  camera.updateProjectionMatrix();
}

function resize() {
  renderer.setSize(viewport.clientWidth, viewport.clientHeight);
  cameraPosition();
}
new ResizeObserver(resize).observe(viewport);

function buildBoard() {
  tooltip.hidden = true;
  const x = (game.rows[0].length - 1) / 2, z = (game.rows.length - 1) / 2;
  sun.position.set(x - 5, 13, z + 8);
  sun.target.position.set(x, 0, z);
  clear(stage);
  buildTiles(stage, game, tileObjects);
  for (const [key, item] of tileObjects) {
    item.group.userData.tile = item;
    if (item.marker && game.state.cells.some(cell => cell.join(',') === key)
        && (item.tile === 'o' || game.state.orientation === 'standing')) item.marker.position.y = -.045;
  }
  if (sceneryLevel !== game.level) {
    clear(scenery);
    buildScenery(scenery, game);
    sceneryLevel = game.level;
  }
}

function buildPieces(state = game.state, status = game.status) {
  clear(pieces);
  if (status === 'won' || status === 'lost') return;
  if (state.split) {
    state.cells.forEach(([r, c], i) => {
      const cube = box(pieces, c, .5, r, .985, 1, .985, i === state.active ? palette.block : palette.inactiveBlock);
      if (i === state.active) {
        const edges = new THREE.LineSegments(new THREE.EdgesGeometry(cube.geometry), new THREE.LineBasicMaterial({ color: 0xeee7ff }));
        cube.add(edges);
      }
    });
  } else {
    const [r, c] = state.cells[0];
    const horizontal = state.orientation === 'horizontal';
    const vertical = state.orientation === 'vertical';
    box(pieces, c + (horizontal ? .5 : 0), state.orientation === 'standing' ? 1 : .5,
        r + (vertical ? .5 : 0), horizontal ? 1.985 : .985, state.orientation === 'standing' ? 2 : 1,
        vertical ? 1.985 : .985, palette.block);
  }
}

function updateUI() {
  testcasePanel?.setBusy(busy || replaying);
  $('#moves').textContent = String(game.moves);
  const bridgeTotal = new Set(game.bridge_cells.map(([, group]) => group)).size;
  $('#bridge-count').textContent = bridgeTotal ? `${game.state.bridges.length} / ${bridgeTotal}` : '—';
  $('#status').textContent = game.message === game.description ? 'Chọn một thuật toán để giải màn hiện tại.' : game.message;
  $('#stage-name').textContent = game.levels.find(level => level.id === game.level).name;
  $('#current-stage').textContent = 'Màn ' + String(game.levels.findIndex(level => level.id === game.level)+1).padStart(2,'0') + ' · ' + $('#stage-name').textContent;
  $('#level-description').textContent = game.description;
  $('.chapter').textContent = String(game.levels.findIndex(level => level.id === game.level)+1).padStart(2,'0') + ' / ' + game.levels.length;
  $('#block-state').textContent = { standing: 'Đứng', horizontal: 'Nằm ngang', vertical: 'Nằm dọc', split: 'Đã tách' }[game.state.orientation];
  $('#orientation').textContent = { standing: 'KHỐI ĐỨNG', horizontal: 'NẰM NGANG', vertical: 'NẰM DỌC', split: 'HAI KHỐI CON' }[game.state.orientation];
  if (game.state.split) $('#orientation').textContent += ` · ĐANG CHỌN ${game.state.active+1}/2`;
  const terminal = game.status !== 'playing';
  const canAdvance = game.status === 'won' && !!nextLevel(game.levels, game.level);
  $('#overlay-next').hidden = !canAdvance;
  $('#overlay').hidden = !terminal;
  $('#overlay').classList.toggle('celebrating',game.status === 'won');
  $('#overlay').dataset.result = game.status;
  if (terminal) {
    $('#result-icon').textContent = game.status === 'won' ? '✓' : '↺';
    $('#result-title').textContent = game.status === 'won' ? 'Hoàn thành màn chơi' : 'Khối đã rơi';
    $('#overlay-restart').classList.toggle('primary',game.status === 'lost');
    $('#overlay-restart').classList.toggle('secondary',game.status === 'won');
    $('#result-copy').textContent = game.status === 'won' ?
      (canAdvance ? `Hoàn thành trong ${game.moves} thao tác. Sẵn sàng cho màn tiếp theo?` : `Hoàn thành trong ${game.moves} thao tác. Bạn đã vượt qua màn cuối!`) : game.message;
  }
  document.querySelectorAll('[data-action]').forEach(button => {
    button.disabled = busy || replaying || terminal || (button.dataset.action === 'switch' && !game.state.split);
  });
  document.querySelectorAll('[data-solver]').forEach(button => button.disabled = busy || replaying || terminal);
  for (const id of ['restart', 'fresh-game', 'level', 'overlay-restart', 'overlay-next']) $( '#' + id).disabled = busy || replaying;
  $('#previous-level').disabled = busy || replaying || !adjacentLevel(game.levels, game.level, -1);
  $('#next-level').disabled = busy || replaying || !nextLevel(game.levels, game.level);
  const hasNextStep = !!path && replayIndex < path.length && !terminal;
  $('#replay').disabled = $('#step-replay').disabled = busy || replaying || !hasNextStep;
  $('#replay').hidden = replaying;
  $('#replay-progress').hidden = !path;
  $('#replay-count').textContent = `${replayIndex} / ${path?.length ?? 0}`;
  $('#replay-bar').max = path?.length || 1;
  $('#replay-bar').value = replayIndex;
  $('#stop-replay').hidden = !replaying;
  $('#stop-replay').disabled = stopRequested;
  $('#stop-replay').textContent = stopRequested ? 'Đang dừng…' : '■ Dừng lời giải';
}

async function api(endpoint, data) {
  const response = await fetch('/api/' + endpoint, data === undefined ? {} : {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data)
  });
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || 'Không thể kết nối engine.');
  return result;
}

function report(error) {
  game.message = 'Có lỗi: ' + error.message + '. Hãy kiểm tra server Python rồi thử lại.';
  $('#status').textContent = game.message;
}

function invalidateSolution() {
  path = null;
  replayIndex = 0;
  $('#metrics').querySelectorAll('b').forEach(value => value.textContent = '—');
  document.querySelectorAll('[data-solver]').forEach(button => button.classList.remove('selected'));
}

function tween(seconds, frame) {
  if (reducedMotion) { frame(1); return Promise.resolve(); }
  return new Promise(resolve => {
    const started = performance.now();
    animation = now => {
      const t = Math.min(1, (now-started) / (seconds*1000));
      frame(t);
      if (t === 1) { animation = null; resolve(); }
    };
  });
}

async function animateMove(before, after, action) {
  if (action === 'switch' || !pieces.children.length) return;
  const dr = action === 'up' ? -1 : action === 'down' ? 1 : 0;
  const dc = action === 'left' ? -1 : action === 'right' ? 1 : 0;
  const object = before.split ? pieces.children[before.active] : pieces.children[0];
  const start = object.position.clone();
  const info = after.transition;
  if (!info?.landing) return;
  const effects = tileEffects(after);
  {
    const size = object.geometry.parameters;
    const pivot = new THREE.Group();
    // Roll around the grid edge at floor height; resting blocks have no air gap.
    const inset = (1-.985)/2;
    pivot.position.set(start.x+dc*(size.width/2+inset), 0, start.z+dr*(size.depth/2+inset));
    pieces.add(pivot);
    pivot.attach(object);
    await tween(before.split ? .20 : .27, t => {
      const eased = t*t*(3-2*t);
      pivot.rotation.x = dr*eased*Math.PI/2;
      pivot.rotation.z = -dc*eased*Math.PI/2;
      effects.frame(Math.max(0,(t-.4)/.6));
    });
    pieces.attach(object);
    pieces.remove(pivot);
  }
  effects.dispose();
  if (after.status === 'lost') {
    const plan = fallPlan(info.landing, info.support, action);
    const center = object.position.toArray();
    const base = object.quaternion.clone();
    const axis = new THREE.Vector3(plan.direction[1],0,-plan.direction[0]);
    const motion = createFallMotion(plan,center);
    const fallingTiles = (info.fallen ?? []).map(cell => tileObjects.get(cell.join(',')))
      .filter(Boolean).map(item => ({model:item.model,start:item.model.position.clone()}));
    await tween(plan.mode === 'edge' ? .75 : .42, t => {
      const pose = motion(t*(plan.mode === 'edge' ? 1.7 : 1));
      object.position.fromArray(pose.position);
      object.quaternion.copy(new THREE.Quaternion().setFromAxisAngle(axis,pose.angle).multiply(base));
      for (const {model,start} of fallingTiles) {
        model.position.set(start.x+pose.position[0]-center[0],start.y+pose.position[1]-center[1],
                           start.z+pose.position[2]-center[2]);
      }
    });
    return;
  }
  if (info.teleport) {
    const sourceY = object.position.y;
    await tween(.20, t => { object.scale.setScalar(1-t*.95); object.position.y = sourceY-t*.65; });
    buildPieces(after.state, 'playing');
    const arriving = pieces.children.map(piece => ({piece, y:piece.position.y}));
    await tween(.36, t => arriving.forEach(({piece,y}) => {
      piece.scale.setScalar(.05+.95*t);
      piece.position.y = y+(1-t)*.7;
    }));
  } else if (before.split && !after.state.split) {
    const joining = pieces.children.map(piece => ({piece, start:piece.position.clone()}));
    const midpoint = joining[0].start.clone().add(joining[1].start).multiplyScalar(.5);
    await tween(.24, t => joining.forEach(({piece,start}) => {
      const ease = Math.sin(t*Math.PI);
      piece.position.copy(start).addScaledVector(start.clone().sub(midpoint), .12*ease);
      piece.position.y += .12*ease;
      piece.scale.setScalar(1+.04*t);
    }));
    buildPieces(after.state,'playing');
    await tween(.20,t => { pieces.children[0].scale.y = 1+.10*Math.sin(t*Math.PI); });
  }
  if (after.status === 'won') {
    const targets = pieces.children.map(piece => ({piece,y:piece.position.y}));
    for (const {piece} of targets) {
      piece.material.transparent = true;
      piece.material.depthWrite = false;
      piece.material.clippingPlanes = [new THREE.Plane(new THREE.Vector3(0,1,0),0)];
      piece.castShadow = false;
    }
    await tween(.55,t => targets.forEach(({piece,y}) => {
      piece.position.y = y-2.5*t*t;
      piece.material.opacity = 1-t*t;
      piece.visible = t < 1;
    }));
    const cell = after.state.cells[0];
    const flag = buildGoalFlag(tileObjects.get(cell.join(',')).model);
    if (!reducedMotion) {
      victoryEffects = {started:performance.now(),update:buildFireworks(celebration,cell)};
    }
    await tween(.4,t => flag.scale.y = .01+.99*(1-(1-t)**3));
  }
}

function tileEffects(after) {
  const info = after.transition;
  const changed = new Map(info.bridges.map(change => [change.group,change.open]));
  const switches = info.switches.map(event => tileObjects.get(event.cell.join(','))).filter(Boolean);
  const bridges = [...tileObjects.values()].filter(item => item.tile === 'B' && changed.has(item.bridge));
  const fragile = info.failure === 'fragile' ? (info.landing?.cells ?? [])
    .map(cell => tileObjects.get(cell.join(','))).filter(item => item?.tile === 'F') : [];
  const halos = switches.filter(item => item.tile !== 'o').map(item => {
    const halo = new THREE.Mesh(new THREE.RingGeometry(.34,.39,32),
      new THREE.MeshBasicMaterial({color:item.tile === 'x'?0xffdca0:0x9cfff0,transparent:true,side:THREE.DoubleSide}));
    halo.rotation.x = -Math.PI/2;
    halo.position.y = .13;
    item.group.add(halo);
    return halo;
  });
  const transforms = bridges.map(item => ({item,start:item.model.rotation.clone()}));
  return {frame(t) {
    for (const item of switches) if (item.marker) item.marker.position.y = -.065*Math.sin(t*Math.PI/2);
    halos.forEach(halo => { halo.scale.setScalar(1+t*2); halo.material.opacity = 1-t; });
    for (const {item,start} of transforms) {
      const open = changed.get(item.bridge);
      item.model.rotation.x = start.x+((open?0:item.closedRotation[0])-start.x)*t;
      item.model.rotation.z = start.z+((open?0:item.closedRotation[2])-start.z)*t;
    }
    fragile.forEach((item,i) => {
      item.model.rotation.z = (i%2?1:-1)*t*.16;
    });
  }, dispose() {
    halos.forEach(halo => { halo.removeFromParent(); halo.geometry.dispose(); halo.material.dispose(); });
  }};
}

async function move(action, fromReplay = false) {
  if (!game || busy || (replaying && !fromReplay) || game.status !== 'playing') return;
  if (action === 'switch' && !game.state.split) return;
  busy = true;
  tooltip.hidden = true;
  if (!fromReplay) invalidateSolution();
  updateUI();
  try {
    const before = game.state;
    const next = await api('move', { action });
    await animateMove(before, next, action);
    game = next;
    buildBoard();
    buildPieces();
    return true;
  } catch (error) {
    report(error);
    return false;
  } finally {
    busy = false;
    updateUI();
  }
}

async function reset(level = game.level) {
  if (busy || replaying) return;
  busy = true;
  invalidateSolution();
  updateUI();
  try {
    game = await api('reset', { level });
    clear(celebration);
    victoryEffects = null;
    $('#level').value = game.level;
    buildBoard();
    buildPieces();
    cameraPosition();
  } catch (error) { report(error); }
  finally { busy = false; updateUI(); }
}

document.querySelectorAll('[data-action]').forEach(button => button.addEventListener('click', () => {
  viewport.focus();
  move(button.dataset.action);
}));
$('#restart').onclick = () => reset();
$('#fresh-game').onclick = () => reset(game.levels[0].id);
function changeLevel(direction) {
  if (!game || busy || replaying) return;
  const target = adjacentLevel(game.levels, game.level, direction);
  if (target) reset(target.id);
}
$('#previous-level').onclick = () => changeLevel(-1);
$('#next-level').onclick = () => changeLevel(1);
$('#overlay-restart').onclick = () => reset();
$('#overlay-next').onclick = () => {
  const next = nextLevel(game.levels, game.level);
  if (game.status === 'won' && next) reset(next.id);
};
$('#level').onchange = event => reset(event.target.value);
$('#help').onclick = () => {
  $('#instructions').open = !$('#instructions').open;
  $('#instructions').scrollIntoView({ behavior: reducedMotion ? 'instant' : 'smooth', block: 'nearest' });
};
const keys = { ArrowUp: 'up', ArrowDown: 'down', ArrowLeft: 'left', ArrowRight: 'right',
               w: 'up', s: 'down', a: 'left', d: 'right', ' ': 'switch' };
window.addEventListener('keydown', event => {
  if (event.ctrlKey || event.metaKey || event.altKey || event.target.isContentEditable ||
      event.target.closest('select, input, textarea')) return;
  const key = event.key.length === 1 ? event.key.toLowerCase() : event.key;
  // Space keeps its native activation behavior on focused controls.
  if (key === ' ' && event.target.closest('button, a, summary')) return;
  if (keys[key]) { event.preventDefault(); if (!event.repeat) move(keys[key]); }
  if (key === 'r' && game) reset();
  if ((key === 'n' || key === 'p') && !event.repeat) changeLevel(key === 'n' ? 1 : -1);
});

async function findSolution(algorithm) {
  document.querySelectorAll('[data-solver]').forEach(button => button.classList.toggle('selected', button.dataset.solver === algorithm));
  const { result } = await api('solve', { algorithm });
  $('#search-time').textContent = result.time_ms + ' ms';
  $('#search-memory').textContent = result.peak_kb + ' KiB';
  $('#search-nodes').textContent = result.expanded.toLocaleString('vi-VN');
  $('#search-length').textContent = result.length === null ? '—' : result.length + ' nước';
  $('#search-cost').textContent = result.cost === null ? '—' : String(result.cost);
  $('#search-result').textContent = {solved:'Tìm thấy',timeout:'Hết giờ',no_solution:'Không có'}[result.status] ?? '—';
  path = result.status === 'solved' ? result.actions : null;
  replayIndex = 0;
  game.message = result.status === 'solved' ? `Tìm thấy lời giải gồm ${result.length} thao tác.` :
    result.status === 'timeout' ? 'Đã hết thời gian tìm kiếm.' : 'Không có đường đến đích từ trạng thái này.';
  return result;
}
document.querySelectorAll('[data-solver]').forEach(button => button.onclick = async () => {
  if (busy || replaying) return;
  busy = true;
  invalidateSolution();
  updateUI();
  $('#status').textContent = 'Đang tìm đường bằng ' + button.textContent + '…';
  document.querySelectorAll('[data-solver]').forEach(b => b.classList.toggle('selected', b === button));
  try {
    await findSolution(button.dataset.solver);
  } catch (error) { game.message = error.message; $('#search-result').textContent = 'Lỗi'; }
  finally { busy = false; updateUI(); }
});
$('#replay').onclick = async () => {
  if (!path || busy || replaying) return;
  stopRequested = false;
  replaying = true;
  updateUI();
  try {
    while (path && replayIndex < path.length) {
      if (stopRequested || game.status !== 'playing') break;
      if (!await move(path[replayIndex], true)) break;
      replayIndex += 1;
      updateUI();
    }
  } finally {
    if (stopRequested && game.status === 'playing') game.message = 'Đã dừng lời giải. Nhấn Phát lại để tiếp tục hoặc tự điều khiển khối.';
    replaying = false;
    updateUI();
  }
};
$('#stop-replay').onclick = () => {
  stopRequested = true;
  updateUI();
};
$('#step-replay').onclick = async () => {
  if (!path || busy || replaying || replayIndex >= path.length || game.status !== 'playing') return;
  if (await move(path[replayIndex], true)) replayIndex += 1;
  updateUI();
};

const raycaster = new THREE.Raycaster();
function hits(event, objects) {
  const bounds = renderer.domElement.getBoundingClientRect();
  raycaster.setFromCamera(new THREE.Vector2(
    (event.clientX-bounds.left)/bounds.width*2-1,
    -(event.clientY-bounds.top)/bounds.height*2+1), camera);
  return raycaster.intersectObjects(objects,true);
}

function showTileHelp(event) {
  tooltip.hidden = true;
  if (!game || busy) return;
  const hit = hits(event,stage.children).find(hit => hit.object.isMesh);
  let object = hit?.object;
  while (object && !object.userData.tile) object = object.parent;
  const item = object?.userData.tile;
  if (!item || !tileHelp[item.tile]) return;
  tooltip.textContent = tileHelp[item.tile] + (item.bridge ?
    (game.state.bridges.includes(item.bridge) ? ' Hiện đang mở.' : ' Hiện đang đóng.') : '');
  tooltip.hidden = false;
  tooltip.style.left = Math.max(8,Math.min(event.clientX+14,window.innerWidth-tooltip.offsetWidth-8))+'px';
  tooltip.style.top = Math.max(8,Math.min(event.clientY+14,window.innerHeight-tooltip.offsetHeight-8))+'px';
}

let dragging = null;
viewport.addEventListener('pointerdown', event => {
  if (event.button !== 0) return;
  tooltip.hidden = true;
  dragging = { x: event.clientX, y: event.clientY, startX:event.clientX, startY:event.clientY, moved:false };
  viewport.setPointerCapture(event.pointerId);
  viewport.focus();
});
viewport.addEventListener('pointermove', event => {
  if (!dragging) { showTileHelp(event); return; }
  dragging.moved ||= Math.hypot(event.clientX-dragging.startX,event.clientY-dragging.startY)>4;
  if (!dragging.moved) return;
  yaw = Math.max(-Math.PI/4, Math.min(Math.PI/4, yaw - (event.clientX - dragging.x) * .006));
  pitch = Math.max(.35, Math.min(1.4, pitch + (event.clientY - dragging.y) * .006));
  dragging.x = event.clientX;
  dragging.y = event.clientY;
  cameraPosition();
});
viewport.addEventListener('pointerup', event => {
  const click = dragging && !dragging.moved;
  dragging = null;
  if (viewport.hasPointerCapture(event.pointerId)) viewport.releasePointerCapture(event.pointerId);
  if (!click || busy || replaying) return;
  showTileHelp(event);
  if (!game?.state.split || game.status !== 'playing') return;
  const hit = hits(event,pieces.children).find(hit => hit.object.isMesh);
  let object = hit?.object;
  while (object && object.parent !== pieces) object = object.parent;
  const index = pieces.children.indexOf(object);
  if (index >= 0 && index !== game.state.active) move('switch');
});
viewport.addEventListener('pointercancel', () => dragging = null);
viewport.addEventListener('pointerleave', () => tooltip.hidden = true);
viewport.addEventListener('wheel', event => {
  event.preventDefault();
  tooltip.hidden = true;
  zoom = Math.max(.65, Math.min(1.8, zoom - event.deltaY * .001));
  cameraPosition();
}, { passive: false });
$('#camera-reset').onclick = () => { tooltip.hidden = true; yaw = .40; pitch = .83; zoom = .86; cameraPosition(); };

function render(now) {
  animation?.(now);
  if (victoryEffects && !victoryEffects.update((now-victoryEffects.started)/1000)) {
    clear(celebration);
    victoryEffects = null;
  }
  renderer.render(scene, camera);
}
renderer.setAnimationLoop(render);
document.addEventListener('visibilitychange', () => renderer.setAnimationLoop(document.hidden ? null : render));

game = await api('game');
$('#level').replaceChildren(...game.levels.map(level => {
  const option = document.createElement('option');
  option.value = level.id;
  option.textContent = level.name;
  return option;
}));
$('#level').value = game.level;
buildBoard();
buildPieces();
resize();
updateUI();
testcasePanel = await initTestcases(api, running => { busy = running; updateUI(); }, level => reset(level));
updateUI();
