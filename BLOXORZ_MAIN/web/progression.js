export function nextLevel(levels, currentId) {
  return adjacentLevel(levels, currentId, 1);
}

export function adjacentLevel(levels, currentId, direction) {
  const index = levels.findIndex(level => level.id === currentId);
  return index < 0 ? undefined : levels[index + direction];
}
