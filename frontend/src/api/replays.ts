import {request,post} from './client';import type {ReplayPlan,ReplayRun} from '../types/domain';
export const listPlans=()=>request<ReplayPlan[]>('/replays/plans');
export const createPlan=(data:unknown)=>post<ReplayPlan>('/replays/plans',data);
export const listRuns=()=>request<ReplayRun[]>('/replays/runs');
export const createRun=(data:unknown)=>post<ReplayRun>('/replays/runs',data);
