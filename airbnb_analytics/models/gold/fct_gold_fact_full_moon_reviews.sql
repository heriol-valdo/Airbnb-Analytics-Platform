-- models/gold/fact_full_moon_reviews.sql
-- Avis survenant les nuits de pleine lune (analyse métier spécialisée)

{{ config(materialized='table', schema='gold') }}

SELECT
    r.listing_id,
    l.listing_name,
    l.room_type,
    l.host_id,
    h.host_name,

    r.review_date,
    fm.full_moon_date,
    DATEDIFF('day', fm.full_moon_date, r.review_date) AS days_after_full_moon,

    r.reviewer_name,
    r.review_text,
    r.sentiment,
    CASE WHEN r.sentiment = 'positive' THEN 1 ELSE 0 END AS is_positive,

    LENGTH(r.review_text) AS text_length,

    CURRENT_TIMESTAMP AS dbt_loaded_at
FROM {{ ref('fct_silver_reviews') }} r
LEFT JOIN {{ ref('fct_silver_listings') }} l
    ON r.listing_id = l.listing_id
LEFT JOIN {{ ref('fct_silver_hosts') }} h
    ON l.host_id = h.host_id
LEFT JOIN {{ ref('fct_silver_full_moon_dates') }} fm
    ON CAST(r.review_date AS DATE) = fm.full_moon_date
WHERE fm.full_moon_date IS NOT NULL
