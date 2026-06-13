-- models/bronze/stg_bronze_reviews.sql

{{ config(
    materialized='table',
    schema='bronze'
) }}

SELECT
    listing_id,
    date,
    reviewer_name,
    comments,
    sentiment
FROM {{ ref('reviews') }}