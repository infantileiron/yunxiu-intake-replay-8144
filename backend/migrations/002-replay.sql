-- Replay tables (replay_plans, replay_runs) are created by SQLAlchemy metadata
-- on first demo seed, same as 001-initial. ReplayRun.snapshot freezes the samples
-- and window capabilities used, so later plan/dataset changes never alter old results.
-- Existing deployments require reviewed ALTER migrations before other model changes.
SELECT 1;
