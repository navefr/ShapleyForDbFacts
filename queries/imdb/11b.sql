SELECT 
    cn.name, 
    save_circuit(provenance(), 'company_name_id', '{path}') 
FROM 
    company_name AS cn, 
    company_type AS ct, 
    keyword AS k, 
    link_type AS lt, 
    movie_companies AS mc, 
    movie_keyword AS mk, 
    movie_link AS ml, 
    title AS t 
WHERE 
    cn.country_code !='[pl]' 
    AND (cn.name LIKE '%Film%' OR cn.name LIKE '%Warner%') 
    AND ct.kind ='production companies' 
    AND k.keyword ='sequel' 
    AND lt.link LIKE '%follows%' 
    AND mc.note IS NULL 
    AND t.production_year  = 1998 
    AND t.title like '%Money%' 
    AND lt.id = ml.link_type_id 
    AND ml.movie_id = t.id 
    AND t.id = mk.movie_id 
    AND mk.keyword_id = k.id
    AND t.id = mc.movie_id 
    AND mc.company_type_id = ct.id
    AND mc.company_id = cn.id
    AND ml.movie_id = mk.movie_id 
    AND ml.movie_id = mc.movie_id 
    AND mk.movie_id = mc.movie_id 
GROUP BY 
    cn.name;