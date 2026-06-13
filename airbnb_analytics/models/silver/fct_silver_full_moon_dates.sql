-- models/silver/silver_full_moon_dates.sql

{{ config(materialized='table', schema='silver') }}

SELECT
    CAST(full_moon_date AS DATE) AS full_moon_date,

    CURRENT_TIMESTAMP AS dbt_loaded_at
FROM {{ ref('stg_bronze_full_moon_dates') }}