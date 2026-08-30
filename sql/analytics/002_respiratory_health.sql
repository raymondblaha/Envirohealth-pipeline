CREATE OR REPLACE VIEW analytics.respiratory_health AS
SELECT
    county_fips,
    year,
    'AgeAdjPrv'::text AS data_value_type_id,
    MAX(estimate) FILTER (WHERE measure_id = 'CASTHMA') AS current_asthma_prevalence,
    MAX(lower_ci) FILTER (WHERE measure_id = 'CASTHMA') AS current_asthma_lower_ci,
    MAX(upper_ci) FILTER (WHERE measure_id = 'CASTHMA') AS current_asthma_upper_ci,
    MAX(estimate) FILTER (WHERE measure_id = 'COPD') AS copd_prevalence,
    MAX(lower_ci) FILTER (WHERE measure_id = 'COPD') AS copd_lower_ci,
    MAX(upper_ci) FILTER (WHERE measure_id = 'COPD') AS copd_upper_ci
FROM core.county_health
WHERE measure_id IN ('CASTHMA', 'COPD')
  AND data_value_type_id = 'AgeAdjPrv'
GROUP BY county_fips, year;
