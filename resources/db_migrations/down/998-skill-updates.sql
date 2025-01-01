
DROP TRIGGER IF EXISTS v1_volunteer_skills_updated_at ON v1.volunteer_skill;

DROP FUNCTION IF EXISTS volunteer_skills_last_updated_at;

DROP TABLE IF EXISTS v1.volunteer_skill_update;

ALTER TABLE v1.volunteer_skill DROP COLUMN IF EXISTS created_at;

DROP TRIGGER IF EXISTS v1_skill_updated_at ON v1.skill;

ALTER TABLE v1.skill DROP COLUMN IF EXISTS updated_at;
ALTER TABLE v1.skill DROP COLUMN IF EXISTS created_at;

DROP TRIGGER IF EXISTS v1_volunteer_updated_at ON v1.volunteer;

ALTER TABLE v1.volunteer DROP COLUMN IF EXISTS updated_at;
ALTER TABLE v1.volunteer DROP COLUMN IF EXISTS created_at;

DROP FUNCTION IF EXISTS set_updated_at;
