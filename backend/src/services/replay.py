import heapq,math,statistics
from collections import deque
def replay(samples,windows):
 """观测重放：按观测顺序累加到达间隔、沿用服务时长，逐窗按可办类别派样。

 规则：同刻到达与完工先结清，再让空窗尽量多开办候办样本；候办按久等优先，
 平局按窗口编号；在办不抢占；没有任何窗口可办的样本单列，不计入等待统计。"""
 if not samples:raise ValueError("重放样本为空")
 if not windows:raise ValueError("重放至少需要一个窗口")
 numbers=[w["window"] for w in windows]
 if len(set(numbers))!=len(numbers):raise ValueError("窗口编号重复")
 caps=[]
 for w in windows:
  if not w.get("categories"):raise ValueError("每个窗口至少配置一个可办类别")
  caps.append(set(w["categories"]))
 norm=[];t=0.0
 for i,s in enumerate(samples):
  ia=s.get("interarrival_minutes");sv=s.get("service_minutes")
  sid=str(s.get("sample_id") or f"#{i+1}")
  if not isinstance(ia,(int,float)) or not math.isfinite(ia) or ia<=0:raise ValueError(f"样本{sid}到达间隔须为有限正数")
  if not isinstance(sv,(int,float)) or not math.isfinite(sv) or sv<=0:raise ValueError(f"样本{sid}服务时长须为有限正数")
  t=round(t+ia,9)
  norm.append({"seq":i+1,"sample_id":sid,"category":str(s.get("category") or "常规"),"arrival":t,"service":sv})
 servable={cat:any(cat in c for c in caps) for cat in {s["category"] for s in norm}}
 records=[None]*len(norm);queues={}
 for i,s in enumerate(norm):
  if servable[s["category"]]:queues.setdefault(s["category"],deque())
  else:records[i]={"seq":s["seq"],"sample_id":s["sample_id"],"category":s["category"],"arrival":s["arrival"],"wait":None,"start":None,"end":None,"window":None,"status":"unhandled","reason":"无可办窗口"}
 idle=sorted(range(len(windows)),key=lambda k:numbers[k]);completions=[];ai=0;queued=0;n=len(norm)
 while ai<n or queued or completions:
  future=[norm[ai]["arrival"]] if ai<n else []
  if completions:future.append(completions[0][0])
  if not future:break
  clock=min(future)
  while completions and completions[0][0]<=clock:idle.append(heapq.heappop(completions)[1])
  idle.sort(key=lambda k:numbers[k])
  while ai<n and norm[ai]["arrival"]<=clock:
   if servable[norm[ai]["category"]]:queues[norm[ai]["category"]].append(ai);queued+=1
   ai+=1
  while idle and queued:
   pick=None
   for cat,q in queues.items():
    if not q:continue
    win=next((k for k in idle if cat in caps[k]),None)
    if win is not None and (pick is None or q[0]<pick[0]):pick=(q[0],cat,win)
   if pick is None:break
   idx,cat,win=pick;queues[cat].popleft();queued-=1;idle.remove(win)
   s=norm[idx];end=round(clock+s["service"],9)
   records[idx]={"seq":s["seq"],"sample_id":s["sample_id"],"category":cat,"arrival":s["arrival"],"wait":round(clock-s["arrival"],9),"start":clock,"end":end,"window":numbers[win],"status":"served","reason":None}
   heapq.heappush(completions,(end,win))
 served=[r for r in records if r["status"]=="served"];waits=[r["wait"] for r in served]
 cats={}
 for r in records:
  c=cats.setdefault(r["category"],{"category":r["category"],"arrived":0,"served":0,"unhandled":0,"waits":[]})
  c["arrived"]+=1
  if r["status"]=="served":c["served"]+=1;c["waits"].append(r["wait"])
  else:c["unhandled"]+=1
 categories=[{"category":c["category"],"arrived":c["arrived"],"served":c["served"],"unhandled":c["unhandled"],"mean_wait_minutes":round(statistics.mean(c["waits"]),3) if c["waits"] else None,"max_wait_minutes":round(max(c["waits"]),3) if c["waits"] else None} for c in cats.values()]
 summary={"total":n,"served":len(served),"unhandled":n-len(served),"mean_wait_minutes":round(statistics.mean(waits),3) if waits else None,"max_wait_minutes":round(max(waits),3) if waits else None,"last_arrival_minutes":norm[-1]["arrival"],"makespan_minutes":max(r["end"] for r in served) if served else 0,"windows":len(windows)}
 notes=["观测重放按观测顺序累加到达间隔、沿用观测服务时长，是对该批样本的确定性重演，不作稳态结论。","同刻到达与完工先结清，再让空窗尽量多开办候办样本：久等优先，平局按窗口编号，在办不抢占。","无可办窗口的样本单列，不计入等待与办理统计。","本结果随样本与窗口能力快照保存，后续方案或观测集调整不改变本次数值。"]
 return {"summary":summary,"categories":categories,"samples":records,"notes":notes}
