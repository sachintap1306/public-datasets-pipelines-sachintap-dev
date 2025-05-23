# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from airflow import DAG
from airflow.providers.google.cloud.transfers import gcs_to_bigquery

default_args = {
    "owner": "Google",
    "depends_on_past": False,
    "start_date": "2021-06-28",
}


with DAG(
    dag_id="covid19_vaccination_search_insights.covid19_vaccination_search_insights",
    default_args=default_args,
    max_active_runs=1,
    schedule_interval="@hourly",
    catchup=False,
    default_view="graph",
) as dag:

    # Task to load global vaccination search insights CSV file from the covid19-open-data bucket to BQ
    gcs_to_bq_vaccination_search_insights = gcs_to_bigquery.GCSToBigQueryOperator(
        task_id="gcs_to_bq_vaccination_search_insights",
        bucket="{{ var.json.covid19_vaccination_search_insights.source_bucket }}",
        source_objects=[
            "{{ var.json.covid19_vaccination_search_insights.source_prefix }}/Global_vaccination_search_insights.csv"
        ],
        source_format="CSV",
        destination_project_dataset_table="covid19_vaccination_search_insights.covid19_vaccination_search_insights",
        skip_leading_rows=1,
        write_disposition="WRITE_TRUNCATE",
        schema_fields=[
            {
                "name": "date",
                "description": "The first day of the week (starting on Monday) on which the searches took place. For example, in the weekly data the row labeled 2021-04-19 represents the search activity for the week of April 19 to April 25, 2021, inclusive. Calendar days start and end at midnight Pacific Standard Time.",
                "type": "DATE",
                "mode": "NULLABLE",
            },
            {
                "name": "country_region",
                "description": "The name of the country in English. For example, United States.",
                "type": "STRING",
                "mode": "NULLABLE",
            },
            {
                "name": "country_region_code",
                "description": "The ISO 3166-1 code for the country. For example, US.",
                "type": "STRING",
                "mode": "NULLABLE",
            },
            {
                "name": "sub_region_1",
                "description": "The name of a region in the country. For example, California.",
                "type": "STRING",
                "mode": "NULLABLE",
            },
            {
                "name": "sub_region_1_code",
                "description": "A country-specific ISO 3166-2 code for the region. For example, US-CA.",
                "type": "STRING",
                "mode": "NULLABLE",
            },
            {
                "name": "sub_region_2",
                "description": "The name (or type) of a region in the country. Typically a subdivision of sub_region_1. For example, Santa Clara County or municipal_borough.",
                "type": "STRING",
                "mode": "NULLABLE",
            },
            {
                "name": "sub_region_2_code",
                "description": "In the US, the FIPS code for a US county (or equivalent). For example, 06085.",
                "type": "STRING",
                "mode": "NULLABLE",
            },
            {
                "name": "sub_region_3",
                "description": "The name (or type) of a region in the country. Typically a subdivision of sub_region_2. For example, Downtown or postal_code.",
                "type": "STRING",
                "mode": "NULLABLE",
            },
            {
                "name": "sub_region_3_code",
                "description": "In the US, the ZIP code. For example 94303.",
                "type": "STRING",
                "mode": "NULLABLE",
            },
            {
                "name": "place_id",
                "description": "The Google place ID for the most-specific subregion. Used in the Google Places API and on Google Maps. For example, ChIJd_Y0eVIvkIARuQyDN0F1LBA.",
                "type": "STRING",
                "mode": "NULLABLE",
            },
            {
                "name": "sni_covid19_vaccination",
                "description": "The scaled normalized interest related to all COVID-19 vaccination for the region and date. For example, 87.02. Empty when data isn't available.",
                "type": "FLOAT",
                "mode": "NULLABLE",
            },
            {
                "name": "sni_vaccination_intent",
                "description": "The scaled normalized interest related to vaccination intent for the region and date. For example, 22.69. Empty when data isn't available.",
                "type": "FLOAT",
                "mode": "NULLABLE",
            },
            {
                "name": "sni_safety_side_effects",
                "description": "The scaled normalized interest related to safety and side effects of the vaccines for the region and date. For example, 17.96. Empty when data isn't available.",
                "type": "FLOAT",
                "mode": "NULLABLE",
            },
        ],
    )

    gcs_to_bq_vaccination_search_insights
