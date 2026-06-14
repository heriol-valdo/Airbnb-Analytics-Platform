-- Test: Vérifier que toutes les dates d'avis sont dans la plage attendue (2009-2021)
-- Échoue si une date est hors de la plage historique du dataset

select
    count(*) as invalid_dates
from {{ ref('fct_silver_reviews') }}
where review_date < '2009-01-01'
   or review_date > '2021-12-31'
having count(*) > 0
