from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import select
from src.config.database import db_session
from src.controllers.auth import current_user,writer
from src.models import ReplayPlan,ReplayRun
from src.schemas.replay import ReplayPlanInput,ReplayRunInput
from src.services import replays as service
from src.utils.serialization import rows,serialize
router=APIRouter(prefix="/replays")
@router.get("/plans")
def plans(db=Depends(db_session),user=Depends(current_user)):return rows(db.scalars(select(ReplayPlan).order_by(ReplayPlan.created_at.desc())))
@router.post("/plans")
def create_plan(payload:ReplayPlanInput,db=Depends(db_session),user=Depends(writer)):return service.create_plan(db,payload)
@router.get("/runs")
def runs(db=Depends(db_session),user=Depends(current_user)):return rows(db.scalars(select(ReplayRun).order_by(ReplayRun.created_at.desc())))
@router.post("/runs")
def create_run(payload:ReplayRunInput,db=Depends(db_session),user=Depends(writer)):return service.create_run(db,payload.plan_id)
@router.get("/runs/{id}")
def run_detail(id:str,db=Depends(db_session),user=Depends(current_user)):
 run=db.get(ReplayRun,id)
 if not run:raise HTTPException(404,"重放运行不存在")
 return serialize(run)
