-- links table
create table public.links (
  id bigint generated by default as identity not null,
  created_at timestamp with time zone not null default now(),
  text text null,
  author_id double precision null,
  constraint links_pkey primary key (id)
) TABLESPACE pg_default;

-- quiz_results table
create table public.quiz_results (
  id bigint generated always as identity not null,
  link_id bigint not null,
  student_id double precision not null,
  correct_answers integer not null,
  total_questions integer not null,
  completed_at timestamp with time zone null default CURRENT_TIMESTAMP,
  average_score integer null,
  constraint quiz_results_pkey primary key (id),
  constraint quiz_results_link_id_fkey foreign KEY (link_id) references links (id),
  constraint quiz_results_student_id_fkey foreign KEY (student_id) references users (user_id)
) TABLESPACE pg_default;

create index IF not exists idx_quiz_results_link_id on public.quiz_results using btree (link_id) TABLESPACE pg_default;

create index IF not exists idx_quiz_results_student_id on public.quiz_results using btree (student_id) TABLESPACE pg_default;

-- users table
create table public.users (
  id bigint generated always as identity not null,
  user_id double precision not null,
  created_at timestamp with time zone null default CURRENT_TIMESTAMP,
  name text not null,
  language text null default 'ru',
  constraint users_pkey primary key (id),
  constraint users_user_id_key unique (user_id)
) TABLESPACE pg_default;