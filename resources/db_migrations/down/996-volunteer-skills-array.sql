DROP VIEW IF EXISTS v1.volunteer_skills;

CREATE OR REPLACE VIEW v1.volunteer_skills AS (
    SELECT v.given_name || ' ' || v.family_name AS volunteer, s.name AS skill
    FROM v1.volunteer_skill vs
             JOIN v1.volunteer v ON vs.volunteer_id = v.id
             JOIN v1.skill s ON vs.skill_id = s.id
);
