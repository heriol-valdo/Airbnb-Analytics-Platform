-- models/bronze/stg_bronze_listings.sql

{{ config(
    materialized='table',
    schema='bronze'
) }}

SELECT
    id,
    listing_url,
    name,
    room_type,
    minimum_nights,
    host_id,
    price,
    created_at,
    updated_at
FROM {{ ref('listings') }}