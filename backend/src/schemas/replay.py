from pydantic import BaseModel,Field,model_validator
from typing import Annotated
Category=Annotated[str,Field(min_length=1,max_length=30)]
class WindowCapability(BaseModel):
 window:int=Field(ge=1,le=12)
 categories:list[Category]=Field(min_length=1,max_length=8)
class ReplayPlanInput(BaseModel):
 name:str=Field(min_length=2,max_length=120)
 dataset_id:str
 windows:list[WindowCapability]=Field(min_length=1,max_length=12)
 @model_validator(mode="after")
 def unique(self):
  if len({w.window for w in self.windows})!=len(self.windows): raise ValueError("窗口编号重复")
  return self
class ReplayRunInput(BaseModel): plan_id:str
