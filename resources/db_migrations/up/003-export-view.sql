CREATE OR REPLACE VIEW v1.volunteer_skills_export AS
(
SELECT v.id                                                                               as volunteer_id,
       v.given_name || ' ' || v.family_name                                               AS volunteer_name,
       TO_CHAR(v.updated_at AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"+00:00"')        as volunteer_updated_at,
       s.id                                                                               as skill_id,
       s.name                                                                             AS skill_name,
       s.description                                                                      AS skill_description,
       TO_CHAR(s.updated_at AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"+00:00"')        as skill_updated_at,
       TO_CHAR(vsu.last_updated_at AT TIME ZONE 'UTC',
               'YYYY-MM-DD"T"HH24:MI:SS"+00:00"')                                         as volunteer_skills_last_updated_at,
       TO_CHAR(NOW() AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"+00:00"')               as query_ts
FROM v1.volunteer_skill vs
       JOIN v1.volunteer v ON vs.volunteer_id = v.id
       JOIN v1.volunteer_skill_update vsu ON vs.volunteer_id = vsu.volunteer_id
       JOIN v1.skill s ON vs.skill_id = s.id
ORDER BY v.id, s.id
  );
