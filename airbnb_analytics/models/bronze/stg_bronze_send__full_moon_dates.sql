-- models/bronze/stg_bronze_full_moon_dates.sql

{{ config(
    materialized='table',
    schema='bronze'
) }}

SELECT
    full_moon_date
FROM {{ ref('seed_full_moon_dates') }}