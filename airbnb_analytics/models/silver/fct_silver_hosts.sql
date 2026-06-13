-- models/silver/fct_silver_hosts.sql

{{ config(materialized='table', schema='silver') }}

SELECT
    id AS host_id,
    name AS host_name,

    -- normalisation booléen (f / t → false / true)
    CASE 
        WHEN is_superhost IN ('t', 'true', 'True', 1) THEN TRUE
        ELSE FALSE
    END AS is_superhost,

    CAST(created_at AS TIMESTAMP) AS created_at,
    CAST(updated_at AS TIMESTAMP) AS updated_at,

    CURRENT_TIMESTAMP AS dbt_loaded_at
FROM {{ ref('stg_bronze_hosts') }}