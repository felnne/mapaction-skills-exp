CREATE OR REPLACE FUNCTION set_updated_at() RETURNS TRIGGER AS
$$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

ALTER TABLE v1.volunteer
  ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW();

CREATE OR REPLACE TRIGGER v1_volunteer_updated_at
  BEFORE INSERT OR UPDATE
  ON v1.volunteer
  FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

ALTER TABLE v1.skill
  ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW();

CREATE OR REPLACE TRIGGER v1_skill_updated_at
  BEFORE INSERT OR UPDATE
  ON v1.skill
  FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

ALTER TABLE v1.volunteer_skill
  ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW();

CREATE TABLE IF NOT EXISTS v1.volunteer_skill_update
(
    volunteer_id INT NOT NULL,
    last_updated_at     TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    PRIMARY KEY (volunteer_id),
    FOREIGN KEY (volunteer_id) REFERENCES v1.volunteer (id)
);

CREATE OR REPLACE FUNCTION volunteer_skills_last_updated_at() RETURNS TRIGGER AS
$$
DECLARE
  vol_id INT;

BEGIN
IF TG_OP = 'INSERT' THEN
  vol_id := NEW.volunteer_id;
ELSIF TG_OP = 'DELETE' THEN
  vol_id := OLD.volunteer_id;
END IF;

INSERT INTO v1.volunteer_skill_update (volunteer_id)
VALUES (vol_id)
ON CONFLICT(volunteer_id)
DO UPDATE SET
  last_updated_at = now();

IF TG_OP = 'INSERT' THEN
  RETURN NEW;
ELSIF TG_OP = 'DELETE' THEN
  RETURN OLD;
END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER v1_volunteer_skills_updated_at
  BEFORE INSERT OR DELETE
  ON v1.volunteer_skill
  FOR EACH ROW
EXECUTE FUNCTION volunteer_skills_last_updated_at();
