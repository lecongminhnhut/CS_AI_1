const G = 9.81;

export function bridgeHinge(rows, r, c) {
  let anchor = [0, -1], nearest = Infinity;
  for (const [dr, dc] of [[-1,0],[0,1],[1,0],[0,-1]]) {
    let distance = 1;
    while (rows[r+dr*distance]?.[c+dc*distance] === 'B') distance++;
    const tile = rows[r+dr*distance]?.[c+dc*distance];
    if (tile && tile !== ' ' && distance < nearest) {
      anchor = [dr,dc];
      nearest = distance;
    }
  }
  const [dr,dc] = anchor;
  return {offset:[dc/2,0,dr/2], rotation:[-dr*Math.PI/2,0,dc*Math.PI/2]};
}

export function fallPlan(landing, support, action) {
  const direction = { up: [0, -1], down: [0, 1], left: [-1, 0], right: [1, 0] }[action];
  if (!landing.split && landing.cells.length === 2 && support.length === 1) {
    const [r, c] = support[0];
    const missing = landing.cells.find(([row, col]) => row !== r || col !== c);
    const dx = missing[1] - c, dz = missing[0] - r;
    return { mode: 'edge', direction: [dx, dz], pivot: [c + dx / 2, 0, r + dz / 2] };
  }
  return { mode: 'free', direction, pivot: null };
}

export function createFallMotion(plan, center) {
  const [dx, dz] = plan.direction;
  if (plan.mode === 'free') {
    return t => ({ position: [center[0] + dx * .55 * t, center[1] - G * t * t / 2,
                              center[2] + dz * .55 * t], angle: t * .7 });
  }
  const [px, py, pz] = plan.pivot;
  const h = center[1] - py;
  const offset = (center[0] - px) * dx + (center[2] - pz) * dz;
  const inertia = 5 / 12 + h * h + offset * offset;
  const dt = 1 / 240;
  const samples = [{ t: 0, angle: 0, omega: .8 }];
  let angle = 0, omega = .8, t = 0;
  // shortcut: fixed edge contact until release; use rigid-body contacts for sliding/friction.
  while (angle < Math.PI / 2 && t < 2) {
    omega += G * (offset * Math.cos(angle) + h * Math.sin(angle)) / inertia * dt;
    angle += omega * dt;
    t += dt;
    samples.push({ t, angle, omega });
  }
  function supportedPose(a) {
    const q = offset * Math.cos(a) + h * Math.sin(a);
    return [center[0] + dx * (q - offset), py - offset * Math.sin(a) + h * Math.cos(a),
            center[2] + dz * (q - offset)];
  }
  const released = samples.at(-1);
  const releasePosition = supportedPose(released.angle);
  const vxz = released.omega * (-offset * Math.sin(released.angle) + h * Math.cos(released.angle));
  const vy = -released.omega * (offset * Math.cos(released.angle) + h * Math.sin(released.angle));
  return elapsed => {
    if (elapsed <= released.t) {
      const i = Math.min(samples.length - 2, Math.floor(Math.max(0, elapsed) / dt));
      const a = samples[i], b = samples[i + 1];
      const theta = a.angle + (b.angle - a.angle) * (elapsed - a.t) / dt;
      return { position: supportedPose(theta), angle: theta };
    }
    const free = elapsed - released.t;
    return { position: [releasePosition[0] + dx * vxz * free,
                        releasePosition[1] + vy * free - G * free * free / 2,
                        releasePosition[2] + dz * vxz * free], angle: released.angle + released.omega * free };
  };
}
