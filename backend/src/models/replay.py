from sqlalchemy import String,JSON,ForeignKey,Text
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class ReplayPlan(Base):
 __tablename__="replay_plans"
 id:Mapped[str]=mapped_column(String(80),primary_key=True)
 name:Mapped[str]=mapped_column(String(160),unique=True)
 dataset_id:Mapped[str]=mapped_column(ForeignKey("arrival_datasets.id"))
 windows:Mapped[list]=mapped_column(JSON)
 created_at:Mapped[str]=mapped_column(String(64))
class ReplayRun(Base):
 __tablename__="replay_runs"
 id:Mapped[str]=mapped_column(String(80),primary_key=True)
 plan_id:Mapped[str]=mapped_column(ForeignKey("replay_plans.id"))
 status:Mapped[str]=mapped_column(String(30))
 snapshot:Mapped[dict]=mapped_column(JSON,default=dict)
 result:Mapped[dict]=mapped_column(JSON,default=dict)
 error:Mapped[str]=mapped_column(Text,default="")
 created_at:Mapped[str]=mapped_column(String(64))
