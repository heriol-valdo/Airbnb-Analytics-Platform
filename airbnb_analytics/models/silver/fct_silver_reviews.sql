-- models/silver/silver_reviews.sql

{{ config(materialized='table', schema='silver') }}

SELECT
    listing_id,

    CAST(date AS TIMESTAMP) AS review_date,

    TRIM(reviewer_name) AS reviewer_name,

    -- nettoyage texte (sécurité analytics)
    TRIM(comments) AS review_text,

    LOWER(sentiment) AS sentiment,

    CURRENT_TIMESTAMP AS dbt_loaded_at
FROM {{ ref('stg_bronze_reviews') }}