-- models/gold/fact_reviews.sql
-- Faits détaillés sur les avis avec contexte hôte et listing

{{ config(materialized='table', schema='gold') }}

SELECT
    ROW_NUMBER() OVER (ORDER BY r.listing_id, r.review_date) AS review_id,

    r.listing_id,
    l.listing_name,
    l.room_type,
    l.price AS listing_price,

    l.host_id,
    h.host_name,
    h.is_superhost,

    r.review_date,
    EXTRACT(YEAR FROM r.review_date) AS review_year,
    EXTRACT(MONTH FROM r.review_date) AS review_month,
    EXTRACT(QUARTER FROM r.review_date) AS review_quarter,
    DAYOFWEEK(r.review_date) AS review_day_of_week,

    r.reviewer_name,
    r.review_text,
    r.sentiment,

    CASE WHEN r.sentiment = 'positive' THEN 1 ELSE 0 END AS is_positive_review,
    LENGTH(r.review_text) AS review_text_length,

    CURRENT_TIMESTAMP AS dbt_loaded_at
FROM {{ ref('fct_silver_reviews') }} r
LEFT JOIN {{ ref('fct_silver_listings') }} l
    ON r.listing_id = l.listing_id
LEFT JOIN {{ ref('fct_silver_hosts') }} h
    ON l.host_id = h.host_id
