-- models/gold/dim_hosts.sql
-- Dimension enrichie des hôtes avec métriques d'activité

{{ config(materialized='table', schema='gold') }}

SELECT
    h.host_id,
    h.host_name,
    h.is_superhost,
    h.created_at AS host_created_at,
    DATEDIFF('day', h.created_at, CURRENT_DATE) AS days_as_host,

    COUNT(DISTINCT l.listing_id) AS total_listings,
    COUNT(DISTINCT r.listing_id) AS listings_with_reviews,

    COALESCE(AVG(l.price), 0) AS avg_listing_price,
    COALESCE(MIN(l.price), 0) AS min_listing_price,
    COALESCE(MAX(l.price), 0) AS max_listing_price,

    COUNT(DISTINCT r.review_date) AS total_reviews,
    COALESCE(AVG(CASE WHEN r.sentiment = 'positive' THEN 1 ELSE 0 END), 0) AS positive_review_rate,

    CURRENT_TIMESTAMP AS dbt_loaded_at
FROM {{ ref('fct_silver_hosts') }} h
LEFT JOIN {{ ref('fct_silver_listings') }} l
    ON h.host_id = l.host_id
LEFT JOIN {{ ref('fct_silver_reviews') }} r
    ON l.listing_id = r.listing_id
GROUP BY
    h.host_id,
    h.host_name,
    h.is_superhost,
    h.created_at
