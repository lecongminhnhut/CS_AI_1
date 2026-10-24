import assert from 'node:assert/strict';
import {runTestcases, resultsCSV} from '../web/testcases.js';

const cases = [{id:'B01',name:'Màn "một", dễ',group:'Cơ bản'}, {id:'M01',name:'Khó',group:'Kết hợp'}];
const algorithms = ['bfs', 'dfs', 'ucs', 'astar'];
const rows = [], calls = [];
const request = async (endpoint, data) => {
  calls.push([endpoint, data]);
  return {result: {algorithm:data.algorithm,status:data.algorithm === 'dfs' ? 'timeout' : 'solved',
    time_ms:0,peak_kb:1,expanded:2,length:data.algorithm === 'dfs' ? null : 0,cost:0,actions:[]}};
};
const count = await runTestcases(cases,request,{algorithms,onResult:row=>rows.push(row),onProgress:()=>{},shouldStop:()=>false});
assert.equal(count,8);
assert.deepEqual(calls.map(([,data])=>data.algorithm),['bfs','dfs','ucs','astar','bfs','dfs','ucs','astar']);
assert.equal(rows[4].testcase,'M01');
const csv = resultsCSV(rows);
assert.ok(csv.startsWith('\uFEFF'));
assert.ok(csv.includes('"Màn ""một"", dễ"'));
assert.ok(csv.includes('"timeout","0","1","2","","0",""'));
assert.ok(csv.includes('"solved","0","1","2","0","0",""'));
assert.ok(resultsCSV([{...rows[0],status:'no_solution',length:null,cost:null}])
  .includes('"no_solution","0","1","2","","",""'));

let stopped = false;
const partial = [];
assert.equal(await runTestcases(cases,request,{
  algorithms,
  onResult: row=>{partial.push(row);stopped=true;},onProgress:()=>{},shouldStop:()=>stopped
}),1);
assert.equal(partial.length,1);
let attempts = 0;
const retained = [];
await assert.rejects(runTestcases(cases,async (...args)=>{
  if (++attempts === 2) throw new Error('Network error');
  return request(...args);
},{algorithms,onResult:row=>retained.push(row),onProgress:()=>{},shouldStop:()=>false}),/Network error/);
assert.equal(retained.length,1);

for (const selected of [['astar'], ['bfs', 'ucs'], []]) {
  const selectedRows = [], progress = [];
  calls.length = 0;
  const completed = await runTestcases(cases, request, {
    algorithms: selected,
    onResult: row=>selectedRows.push(row),
    onProgress: (test, algorithm, done, total)=>progress.push({done, total}),
    shouldStop: ()=>false
  });
  assert.equal(completed, cases.length * selected.length);
  assert.deepEqual(calls.map(([, data])=>data.algorithm), cases.flatMap(()=>selected));
  assert.ok(progress.every(step=>step.total === cases.length * selected.length));
  assert.equal(selectedRows.length, completed);
  assert.ok(selectedRows.every(row=>selected.includes(row.algorithm)));
}
console.log('Testcase queue, stop/error retention, and CSV export passed.');
