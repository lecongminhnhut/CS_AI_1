import * as THREE from './vendor/three.module.js';
import { buildTiles } from './art.js?v=ground-fit';

// Render the same geometry and materials as the board, once per legend item.
// A single temporary renderer produces static images rather than six live scenes.
export function renderTileLegend(boardScene) {
  const renderer = new THREE.WebGLRenderer({antialias:true, alpha:true});
  renderer.setSize(144, 108);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.05;
  const scene = new THREE.Scene();
  boardScene.children.filter(object => object.isLight).forEach(light => {
    const copy = light.clone();
    copy.castShadow = false;
    scene.add(copy);
  });
  const camera = new THREE.OrthographicCamera(-.9,.9,.675,-.675,.1,20);
  camera.position.set(2,4.5,5);
  camera.lookAt(0,-.08,0);
  try {
    for (const holder of document.querySelectorAll('.tile-preview[data-tile]')) {
      const tile = holder.dataset.tile;
      const stage = new THREE.Group();
      scene.add(stage);
      try {
        buildTiles(stage, {
          rows:[tile], status:'playing',
          bridge_cells:tile === 'B' ? [[[0,0],'preview']] : [],
          state:{bridges:tile === 'B' ? ['preview'] : []}
        }, new Map());
        renderer.render(scene,camera);
        const preview = document.createElement('img');
        preview.alt = '';
        preview.width = 48;
        preview.height = 36;
        preview.src = renderer.domElement.toDataURL('image/png');
        holder.replaceChildren(preview);
      } finally {
        scene.remove(stage);
        stage.traverse(object => {
          object.geometry?.dispose();
          object.material?.dispose();
        });
      }
    }
  } finally {
    renderer.dispose();
  }
}
