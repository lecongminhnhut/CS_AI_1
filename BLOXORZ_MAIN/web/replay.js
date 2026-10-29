export function countRolls(actions, end = actions.length) {
  let count = 0;
  for (let index = 0; index < end; index++) {
    if (actions[index] !== 'switch') count++;
  }
  return count;
}

export async function replayNextRoll(actions, index, move) {
  while (index < actions.length) {
    const action = actions[index];
    if (!await move(action)) return {index, moved: false};
    index++;
    if (action !== 'switch') return {index, moved: true};
  }
  return {index, moved: false};
}
