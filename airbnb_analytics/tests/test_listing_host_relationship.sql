-- Test: Vérifier que tous les listings ont un hôte valide
-- Échoue si une listing référence un hôte qui n'existe pas

select
    count(*) as orphaned_listings
from {{ ref('fct_silver_listings') }} listings
left join {{ ref('fct_silver_hosts') }} hosts
    on listings.host_id = hosts.host_id
where hosts.host_id is null
having count(*) > 0
