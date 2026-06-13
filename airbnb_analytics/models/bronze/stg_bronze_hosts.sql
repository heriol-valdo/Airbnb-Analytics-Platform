-- models/bronze/stg_bronze_hosts.sql

{{ config(
    materialized='table',
    schema='bronze'
) }}

SELECT
    id,
    name,
    is_superhost,
    created_at,
    updated_at
FROM {{ ref('hosts') }}