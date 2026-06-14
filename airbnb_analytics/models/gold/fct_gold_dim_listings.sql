-- models/gold/dim_listings.sql
-- Dimension enrichie des listings avec informations détaillées

{{ config(materialized='table', schema='gold') }}

SELECT
    l.listing_id,
    l.listing_name,
    l.listing_url,
    l.room_type,
    l.host_id,
    h.host_name,
    h.is_superhost AS host_is_superhost,

    l.price AS nightly_price,
    l.minimum_nights,

    CASE
        WHEN l.price < 100 THEN 'Budget'
        WHEN l.price < 200 THEN 'Mid-Range'
        WHEN l.price < 400 THEN 'Premium'
        ELSE 'Luxury'
    END AS price_category,

    COUNT(DISTINCT r.review_date) AS total_reviews,
    DATEDIFF('day', l.created_at, CURRENT_DATE) AS days_listed,
    COALESCE(COUNT(DISTINCT r.review_date)::DOUBLE / DATEDIFF('day', l.created_at, CURRENT_DATE), 0) AS reviews_per_day,

    COALESCE(AVG(CASE WHEN r.sentiment = 'positive' THEN 1 ELSE 0 END), 0) AS positive_review_pct,

    l.created_at AS listing_created_at,
    CURRENT_TIMESTAMP AS dbt_loaded_at
FROM {{ ref('fct_silver_listings') }} l
LEFT JOIN {{ ref('fct_silver_hosts') }} h
    ON l.host_id = h.host_id
LEFT JOIN {{ ref('fct_silver_reviews') }} r
    ON l.listing_id = r.listing_id
GROUP BY
    l.listing_id,
    l.listing_name,
    l.listing_url,
    l.room_type,
    l.host_id,
    h.host_name,
    h.is_superhost,
    l.price,
    l.minimum_nights,
    l.created_at
