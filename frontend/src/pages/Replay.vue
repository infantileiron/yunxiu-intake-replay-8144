<script setup lang="ts">
import {ref,computed,watch} from 'vue';
import type {Workspace} from '../stores/workspace';
import PageHeading from '../components/common/PageHeading.vue';
import Notice from '../components/common/Notice.vue';
import Status from '../components/common/Status.vue';
import Empty from '../components/common/Empty.vue';
import {createPlan,createRun} from '../api/replays';
import {useAsync} from '../hooks/useAsync';
import {number} from '../utils/format';
const props=defineProps<{data:Workspace;canWrite:boolean;refresh:()=>Promise<void>}>();
const name=ref(''),datasetId=ref(''),windowCount=ref(3),caps=ref<Record<number,string[]>>({}),selected=ref('');
const dataset=computed(()=>props.data.datasets.find(d=>d.id===datasetId.value)||props.data.datasets[0]);
const categories=computed(()=>[...new Set((dataset.value?.rows||[]).map(r=>r.category||'常规'))]);
const windows=computed(()=>Array.from({length:windowCount.value},(_,i)=>i+1));
watch([categories,windowCount],()=>{const next:Record<string,string[]>={};for(const w of windows.value)next[w]=caps.value[w]?.length?caps.value[w].filter(c=>categories.value.includes(c)):[...categories.value];caps.value=next},{immediate:true});
const run=computed(()=>props.data.replayRuns.find(r=>r.id===selected.value)||props.data.replayRuns[0]);
const result=computed(()=>run.value?.status==='completed'?run.value.result:null);
const served=computed(()=>result.value?result.value.samples.filter(s=>s.status==='served'):[]);
const unhandled=computed(()=>result.value?result.value.samples.filter(s=>s.status==='unhandled'):[]);
const {busy,error,execute}=useAsync();
function toggle(w:number,c:string){const list=caps.value[w]||[];caps.value={...caps.value,[w]:list.includes(c)?list.filter(x=>x!==c):[...list,c]}}
function valid(){return windows.value.every(w=>(caps.value[w]||[]).length>0)}
async function submit(){await execute(async()=>{if(!valid())throw new Error('每个窗口至少勾选一个可办类别');await createPlan({name:name.value,dataset_id:dataset.value?.id,windows:windows.value.map(w=>({window:w,categories:caps.value[w]}))});name.value='';await props.refresh()})}
async function launch(id:string){await execute(async()=>{const r=await createRun({plan_id:id});await props.refresh();selected.value=r.id})}
const capsText=(ws:{window:number;categories:string[]}[])=>[...ws].sort((a,b)=>a.window-b.window).map(w=>`${w.window}号窗·${w.categories.join('/')}`).join('　');
</script>
<template>
<PageHeading code="05 / OBSERVATION REPLAY" title="专窗能办什么，写进方案再重放。" description="样本带业务类别，方案逐窗配置可办类别。按观测顺序累加到达间隔、沿用服务时长，确定性重演这一批观测，不作稳态结论。"/>
<section v-if="canWrite" class="paper"><h2>新建观测重放方案</h2><form class="scenario-form" @submit.prevent="submit"><label>方案名称<input aria-label="方案名称" v-model="name" required minlength="2"/></label><label>观测集<select aria-label="观测集" v-model="datasetId"><option value="" disabled>默认使用最新观测集</option><option v-for="d in data.datasets" :key="d.id" :value="d.id">{{d.name}}</option></select></label><label>窗口数<input aria-label="窗口数" type="number" min="1" max="12" v-model.number="windowCount"/></label><div class="wide"><small>逐窗勾选可办类别（专窗只勾能办的类别，通用窗全勾）</small><div class="window-caps"><div v-for="w in windows" :key="w" class="window-cap"><b>{{w}}号窗</b><label v-for="c in categories" :key="c" class="cap-check"><input type="checkbox" :checked="caps[w]?.includes(c)" @change="toggle(w,c)"/>{{c}}</label></div></div></div><button :disabled="busy||!dataset">保存重放方案</button></form></section>
<Notice v-if="error" error>{{error}}</Notice>
<section class="paper"><h2>已保存重放方案</h2><Empty v-if="!data.replayPlans.length">保存一个逐窗配置可办类别的方案，即可重放观测。</Empty><article v-for="p in data.replayPlans" :key="p.id" class="scenario-row"><div class="counter-number">{{p.windows.length}}<small>WINDOWS</small></div><div class="scenario-detail"><h3>{{p.name}}</h3><p>{{data.datasets.find(d=>d.id===p.dataset_id)?.name||'观测集已移除'}}</p><small>{{capsText(p.windows)}}</small></div><button class="secondary" v-if="canWrite" :disabled="busy" @click="launch(p.id)">运行重放　→</button></article></section>
<section class="paper"><div class="section-heading"><h2>重放结果</h2><span v-if="run">快照：{{run.snapshot.dataset_name}} · {{run.snapshot.samples.length}}条样本 · {{capsText(run.snapshot.windows)}}</span></div><div class="run-selector"><label>重放记录<select aria-label="选择重放记录" :value="run?.id" @change="selected=($event.target as HTMLSelectElement).value"><option v-for="r in data.replayRuns" :key="r.id" :value="r.id">{{data.replayPlans.find(p=>p.id===r.plan_id)?.name||r.snapshot.plan_name}} · {{r.created_at.slice(0,19).replace('T',' ')}}</option></select></label><Status v-if="run" :value="run.status"/></div><Empty v-if="!run">尚无重放记录。</Empty><Notice v-else-if="run.status==='failed'" error>{{run.error}}</Notice><template v-else-if="result">
<Notice>本次为观测重放：确定性重演该批样本，不作稳态结论。结果随样本与窗口能力快照保存，后续配置变化不改变本页数值。</Notice>
<div class="result-metrics"><div><small>到达样本</small><b>{{result.summary.total}}</b><em>末样本 {{number(result.summary.last_arrival_minutes,1)}} 分钟到达</em></div><div class="featured"><small>已办样本</small><b>{{result.summary.served}}</b><em>全部完工于 {{number(result.summary.makespan_minutes,1)}} 分钟</em></div><div><small>未办单列</small><b>{{result.summary.unhandled}}</b><em>无可办窗口</em></div><div><small>平均等待 / 最长</small><b>{{number(result.summary.mean_wait_minutes)}}</b><em>分钟 · 最长 {{number(result.summary.max_wait_minutes)}} 分钟</em></div></div>
<h3>按类别对账</h3><div class="table-scroll"><table><thead><tr><th>业务类别</th><th>到达</th><th>办理</th><th>未办</th><th>对账</th><th>平均等待 / 分钟</th><th>最长等待 / 分钟</th></tr></thead><tbody><tr v-for="c in result.categories" :key="c.category"><td><b>{{c.category}}</b></td><td>{{c.arrived}}</td><td>{{c.served}}</td><td>{{c.unhandled}}</td><td>{{c.arrived===c.served+c.unhandled?'到达 = 办理 + 未办 ✓':'不平 ✗'}}</td><td>{{number(c.mean_wait_minutes)}}</td><td>{{number(c.max_wait_minutes)}}</td></tr><tr><td><b>合计</b></td><td><b>{{result.summary.total}}</b></td><td><b>{{result.summary.served}}</b></td><td><b>{{result.summary.unhandled}}</b></td><td>{{result.summary.total===result.summary.served+result.summary.unhandled?'到达 = 办理 + 未办 ✓':'不平 ✗'}}</td><td>{{number(result.summary.mean_wait_minutes)}}</td><td>{{number(result.summary.max_wait_minutes)}}</td></tr></tbody></table></div>
<template v-if="unhandled.length"><h3 class="replay-sub">未办样本（无可办窗口，单列）</h3><div class="table-scroll"><table><thead><tr><th>匿名样本</th><th>业务类别</th><th>到达 / 分钟</th><th>未办原因</th></tr></thead><tbody><tr v-for="s in unhandled" :key="s.sample_id"><td>{{s.sample_id}}</td><td>{{s.category}}</td><td>{{number(s.arrival,1)}}</td><td>{{s.reason}}</td></tr></tbody></table></div></template>
<h3 class="replay-sub">逐样本办理明细</h3><div class="table-scroll"><table><thead><tr><th>#</th><th>匿名样本</th><th>业务类别</th><th>到达 / 分钟</th><th>等待 / 分钟</th><th>办理窗口</th><th>起止 / 分钟</th></tr></thead><tbody><tr v-for="s in served.slice(0,300)" :key="s.sample_id"><td>{{s.seq}}</td><td>{{s.sample_id}}</td><td>{{s.category}}</td><td>{{number(s.arrival,1)}}</td><td><b>{{number(s.wait)}}</b></td><td>{{s.window}}号窗</td><td>{{number(s.start,1)}}—{{number(s.end,1)}}</td></tr></tbody></table></div><p v-if="served.length>300" class="caption">预览前300条已办样本，共{{served.length}}条。</p>
<h3 class="replay-sub">重放口径</h3><ol class="assumption-list"><li v-for="n in result.notes" :key="n">{{n}}</li></ol>
</template></section>
</template>
