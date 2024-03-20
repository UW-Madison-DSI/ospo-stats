SELECT * FROM wisconsin_repositories
WHERE name NOT LIKE '%Breast%' 
AND name NOT LIKE '%Brest%' 
AND name NOT LIKE 'CS%'
AND description NOT LIKE '{"%'
AND readme_size IS NOT NULL
AND readme_has_images = 1
AND homepage IS NOT NULL
AND license_name IS NOT NULL