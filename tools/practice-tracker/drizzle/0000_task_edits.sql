CREATE TABLE task_edits (
  user_id TEXT NOT NULL,
  task_id TEXT NOT NULL,
  value TEXT NOT NULL,
  PRIMARY KEY (user_id, task_id)
);
