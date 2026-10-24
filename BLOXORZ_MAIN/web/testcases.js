const names = {bfs: 'BFS', dfs: 'DFS/IDS', ucs: 'UCS', astar: 'A*'};
const statuses = {solved: 'Tìm thấy', timeout: 'Hết giờ', no_solution: 'Vô nghiệm'};

export async function runTestcases(cases, request, {algorithms, onResult, onProgress, shouldStop}) {
  let completed = 0;
  for (const test of cases) {
    for (const algorithm of algorithms) {
      if (shouldStop()) return completed;
      onProgress(test, algorithm, completed, cases.length * algorithms.length);
      const {result} = await request('testcase', {level: test.id, algorithm});
      onResult({group: test.group, testcase: test.id, name: test.name, ...result});
      completed += 1;
    }
  }
  return completed;
}

export function resultsCSV(results) {
  const columns = ['group', 'testcase', 'name', 'algorithm', 'status', 'time_ms', 'peak_kb', 'expanded', 'length', 'cost', 'actions'];
  const quote = value => '"' + String(value ?? '').replaceAll('"', '""') + '"';
  return '\uFEFF' + [columns, ...results.map(row => columns.map(key =>
    key === 'actions' ? (row.actions ?? []).join(' ') : row[key]))]
    .map(row => row.map(quote).join(',')).join('\r\n');
}

export async function initTestcases(api, onRunning, openLevel) {
  const $ = id => document.getElementById(id);
  let groups, running = false, busy = false, stop = false, results = [];
  const selected = () => [...$('test-list').querySelectorAll('input:checked')].map(input => input.value);
  const selectedAlgorithms = () => [...$('test-algorithms').querySelectorAll('input:checked')].map(input => input.value);

  function setBusy(value) {
    busy = value;
    const inputs = [...$('test-list').querySelectorAll('input')];
    const count = inputs.filter(input => input.checked).length;
    $('test-group').disabled = $('test-select-all').disabled = busy || running || !groups;
    $('test-algorithms').disabled = busy || running || !groups;
    $('test-run').disabled = busy || running || !count || !selectedAlgorithms().length;
    $('test-select-all').checked = !!count && count === inputs.length;
    $('test-select-all').indeterminate = count > 0 && count < inputs.length;
    $('test-list').querySelectorAll('input, button').forEach(control => control.disabled = busy || running);
    $('test-stop').hidden = !running;
    $('test-stop').disabled = stop;
    $('test-csv').disabled = $('test-json').disabled = !results.length;
  }

  function renderList() {
    const visible = groups.filter(group => $('test-group').value === 'all' || group.id === $('test-group').value);
    $('test-list').replaceChildren();
    for (const group of visible) {
      for (const test of group.cases) {
        const row = document.createElement('div');
        row.title = group.description;
        const label = document.createElement('label');
        const input = document.createElement('input');
        input.type = 'checkbox';
        input.value = test.id;
        input.checked = true;
        input.onchange = () => setBusy(busy);
        label.append(input, document.createTextNode(test.name));
        const open = document.createElement('button');
        open.className = 'secondary';
        open.textContent = 'Mở màn';
        open.setAttribute('aria-label', `Mở màn ${test.name}`);
        open.onclick = () => openLevel(test.id);
        row.append(label, open);
        $('test-list').append(row);
      }
    }
    $('test-status').textContent = visible.map(group => `${group.name}: ${group.description}`).join(' ');
    setBusy(busy);
  }

  function addResult(result) {
    results.push(result);
    const row = document.createElement('tr');
    for (const value of [result.group, result.name, names[result.algorithm], statuses[result.status] ?? result.status,
      result.time_ms, result.peak_kb, result.expanded, result.length, result.cost]) {
      const cell = document.createElement('td');
      cell.textContent = value ?? '—';
      row.append(cell);
    }
    $('test-results').append(row);
    $('test-progress').value = results.length;
    setBusy(busy);
  }

  $('test-select-all').onchange = () => {
    $('test-list').querySelectorAll('input').forEach(input => input.checked = $('test-select-all').checked);
    setBusy(busy);
  };
  $('test-group').onchange = renderList;
  $('test-algorithms').onchange = () => setBusy(busy);
  $('test-stop').onclick = () => {
    stop = true;
    $('test-status').textContent = 'Đang dừng sau lượt hiện tại; kết quả đã chạy vẫn xuất được.';
    setBusy(busy);
  };
  $('test-run').onclick = async () => {
    if (busy || running) return;
    const algorithms = selectedAlgorithms();
    const ids = new Set(selected());
    const cases = groups.flatMap(group => group.cases.filter(test => ids.has(test.id))
      .map(test => ({...test, group: group.name})));
    if (!cases.length || !algorithms.length) return;
    running = true;
    stop = false;
    results = [];
    $('test-results').replaceChildren();
    $('test-progress').hidden = false;
    $('test-progress').value = 0;
    $('test-progress').max = cases.length * algorithms.length;
    onRunning(true);
    setBusy(true);
    try {
      const completed = await runTestcases(cases, api, {
        algorithms,
        onResult: addResult,
        onProgress: (test, algorithm, done, total) => {
          $('test-status').textContent = `${done}/${total} lượt · ${test.name} · đang chạy ${names[algorithm]}…`;
        },
        shouldStop: () => stop
      });
      $('test-status').textContent = `${stop ? 'Đã dừng' : 'Hoàn tất'}: ${completed}/${cases.length * algorithms.length} lượt. Có thể xuất kết quả.`;
    } catch (error) {
      $('test-status').textContent = `Đã dừng do lỗi: ${error.message}. Giữ lại ${results.length} kết quả để xuất.`;
    } finally {
      running = false;
      onRunning(false);
      setBusy(false);
    }
  };

  function download(format) {
    const content = format === 'csv' ? resultsCSV(results) : JSON.stringify({
      exported_at: new Date().toISOString(), timeout_seconds: null, start: 'initial_state', results
    }, null, 2);
    const url = URL.createObjectURL(new Blob([content], {
      type: format === 'csv' ? 'text/csv;charset=utf-8' : 'application/json;charset=utf-8'
    }));
    const link = document.createElement('a');
    link.href = url;
    link.download = `bloxorz-testcases.${format}`;
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  $('test-csv').onclick = () => download('csv');
  $('test-json').onclick = () => download('json');
  try {
    ({groups} = await api('testcases'));
    const count = groups.reduce((total, group) => total + group.cases.length, 0);
    $('testcase-count').textContent = `${groups.length} nhóm · ${count} màn`;
    $('test-group').replaceChildren(...[{id: 'all', name: `Tất cả · ${count} màn`}, ...groups].map(group => {
      const option = document.createElement('option');
      option.value = group.id;
      option.textContent = group.name;
      return option;
    }));
    renderList();
  } catch (error) {
    $('test-status').textContent = `Không tải được testcase: ${error.message}`;
  }
  return {setBusy};
}
