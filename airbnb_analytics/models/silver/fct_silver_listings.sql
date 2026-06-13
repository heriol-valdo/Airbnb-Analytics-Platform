-- models/silver/fct_silver_listings.sql

{{ config(materialized='table', schema='silver') }}

SELECT
    id AS listing_id,
    listing_url,
    name AS listing_name,
    room_type,
    CAST(minimum_nights AS INTEGER) AS minimum_nights,
    host_id,

    -- nettoyage du prix ($90.00 → 90.00)
    CAST(REPLACE(price, '$', '') AS DOUBLE) AS price,

    CAST(created_at AS TIMESTAMP) AS created_at,
    CAST(updated_at AS TIMESTAMP) AS updated_at,

    CURRENT_TIMESTAMP AS dbt_loaded_at
FROM {{ ref('stg_bronze_listings') }}