import uuid
from copy import deepcopy
from fastapi import HTTPException
from sqlalchemy import select
from src.models import ReplayPlan,ReplayRun,ArrivalDataset
from src.services.replay import replay
from src.utils.time import now
from src.utils.serialization import serialize
def create_plan(db,payload):
 if not db.get(ArrivalDataset,payload.dataset_id):raise HTTPException(404,"观测集不存在")
 if db.scalar(select(ReplayPlan).where(ReplayPlan.name==payload.name)):raise HTTPException(409,"重放方案名称已存在")
 item=ReplayPlan(id=str(uuid.uuid4()),created_at=now(),windows=[w.model_dump() for w in payload.windows],**payload.model_dump(exclude={"windows"}));db.add(item);db.commit();return serialize(item)
def create_run(db,plan_id):
 plan=db.get(ReplayPlan,plan_id)
 if not plan:raise HTTPException(404,"重放方案不存在")
 dataset=db.get(ArrivalDataset,plan.dataset_id)
 if not dataset:raise HTTPException(404,"重放方案引用的观测集不存在")
 samples=[{"sample_id":r.get("sample_id"),"category":r.get("category") or "常规","interarrival_minutes":r.get("interarrival_minutes"),"service_minutes":r.get("service_minutes")} for r in dataset.rows]
 snapshot={"dataset_id":dataset.id,"dataset_name":dataset.name,"plan_name":plan.name,"samples":samples,"windows":deepcopy(plan.windows)}
 item=ReplayRun(id=str(uuid.uuid4()),plan_id=plan.id,status="completed",snapshot=snapshot,result={},error="",created_at=now())
 try:item.result=replay(samples,plan.windows)
 except Exception as error:item.status="failed";item.error=str(error)
 db.add(item);db.commit();return serialize(item)
