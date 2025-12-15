SELECT
    p.project_id,
    p.theme,
    p.description,
    cs.cs_date
FROM project p
JOIN commission_schedule cs ON cs.project_id = p.project_id
WHERE cs.cs_date = %(date)s;
