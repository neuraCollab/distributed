-- Ensure compatibility with Cassandra 5.0+
-- Create the keyspace
CREATE KEYSPACE IF NOT EXISTS parser
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}
AND durable_writes = true;

-- Switch to the parser keyspace
USE parser;

-- Create a table for storing task requests
CREATE TABLE IF NOT EXISTS task_requests (
    worker_id text,             -- Worker unique ID
    timestamp timestamp,        -- Time when the task was requested
    has_task boolean,           -- Indicates if a task is assigned
    url text,                   -- URL of the task
    PRIMARY KEY (worker_id)     -- worker_id as the partition key
);

-- Create a table for storing task results
CREATE TABLE IF NOT EXISTS task_results (
    worker_id text,             -- Worker unique ID
    url text,                   -- URL of the task
    result text,                -- Result of the task
    timestamp timestamp,        -- Time when the result was submitted
    PRIMARY KEY (worker_id, url) -- Composite key for uniqueness
);

-- Create a table for storing submitted tasks
CREATE TABLE IF NOT EXISTS submitted_tasks (
    url text PRIMARY KEY,       -- Unique URL for each task
    success boolean,            -- Indicates if the task was successful
    timestamp timestamp         -- Time when the task was submitted
);

-- Create a table for storing acknowledgments
CREATE TABLE IF NOT EXISTS result_acks (
    worker_id text,             -- Worker unique ID
    url text,                   -- URL of the task
    success boolean,            -- Indicates if the acknowledgment was successful
    timestamp timestamp,        -- Time when the acknowledgment was sent
    PRIMARY KEY (worker_id, url) -- Composite key for uniqueness
);

-- Create a table for storing parsed results
CREATE TABLE IF NOT EXISTS parsed_results (
    url text PRIMARY KEY,       -- Unique URL for each parsed result
    links text,                 -- A serialized string of links or JSON format
    time_taken double           -- Time taken to process the URL (in seconds or milliseconds)
);

-- Optional: Create indexes for frequently queried fields
CREATE INDEX IF NOT EXISTS idx_task_requests_url ON task_requests (url);
CREATE INDEX IF NOT EXISTS idx_task_results_timestamp ON task_results (timestamp);
CREATE INDEX IF NOT EXISTS idx_submitted_tasks_success ON submitted_tasks (success);
CREATE INDEX IF NOT EXISTS idx_result_acks_timestamp ON result_acks (timestamp);
CREATE INDEX IF NOT EXISTS idx_parsed_results_time_taken ON parsed_results (time_taken); -- Optional index for time_taken
