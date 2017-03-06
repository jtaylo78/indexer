-- Table: public.events

-- DROP TABLE public.events;

CREATE TABLE public.events
(
  id bigint NOT NULL DEFAULT nextval('events_id_seq'::regclass),
  event_full text,
  attr_timestamp bigint DEFAULT date_part('epoch'::text, now()),
  event_type text,
  event_id integer DEFAULT 0,
  integrity_level text,
  utc_time date,
  source text,
  parent_command_line text,
  parent_image text,
  parent_process_guid text,
  hashes text,
  "user" text,
  current_directory text,
  command_line text,
  image text,
  process_guid text,
  user_2 text,
  logon_type text,
  domain text,
  sphinx_json text
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.events
  OWNER TO postgres;

-- Index: public.index_id_events

-- DROP INDEX public.index_id_events;

CREATE INDEX index_id_events
  ON public.events
  USING hash
  (id);

