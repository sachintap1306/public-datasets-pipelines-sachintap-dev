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
from airflow.providers.cncf.kubernetes.operators import kubernetes_pod
from airflow.providers.google.cloud.transfers import gcs_to_bigquery

default_args = {
    "owner": "Google",
    "depends_on_past": False,
    "start_date": "2021-03-01",
}


with DAG(
    dag_id="fda_food.food_enforcement",
    default_args=default_args,
    max_active_runs=1,
    schedule_interval="@daily",
    catchup=False,
    default_view="graph",
) as dag:

    # Run CSV transform within kubernetes pod
    transform_csv = kubernetes_pod.KubernetesPodOperator(
        task_id="transform_csv",
        name="food_enforcement",
        namespace="composer-user-workloads",
        service_account_name="default",
        config_file="/home/airflow/composer_kube_config",
        image_pull_policy="Always",
        image="{{ var.json.fda_food.container_registry.run_csv_transform_kub }}",
        env_vars={
            "PIPELINE": "food enforcement",
            "SOURCE_URL": "https://download.open.fda.gov/food/enforcement/food-enforcement-0001-of-0001.json.zip",
            "SOURCE_FILE": "files/data.csv",
            "TARGET_FILE": "files/data_output.csv",
            "CHUNKSIZE": "750000",
            "TARGET_GCS_BUCKET": "{{ var.value.composer_bucket }}",
            "TARGET_GCS_PATH": "data/fda_food/food_enforcement/files/data_output.csv",
            "DATA_NAMES": '[ "status", "city", "state", "country", "classification",\n  "openfda", "product_type", "event_id", "recalling_firm", "address_1",\n  "address_2", "postal_code", "voluntary_mandated", "initial_firm_notification", "distribution_pattern",\n  "recall_number", "product_description", "product_quantity", "reason_for_recall", "recall_initiation_date",\n  "center_classification_date", "report_date", "code_info", "more_code_info", "termination_date" ]',
            "DATA_DTYPES": '{ "status": "str", "city": "str", "state": "str", "country": "str", "classification": "str",\n  "openfda": "str", "product_type": "str", "event_id": "str", "recalling_firm": "str", "address_1": "str",\n  "address_2": "str", "postal_code": "str", "voluntary_mandated": "str", "initial_firm_notification": "str", "distribution_pattern": "str",\n  "recall_number": "str", "product_description": "str", "product_quantity": "str", "reason_for_recall": "str", "recall_initiation_date": "str",\n  "center_classification_date": "str", "report_date": "str", "code_info": "str", "more_code_info": "str", "termination_date": "str" }',
            "RENAME_MAPPINGS": "{ }",
            "REORDER_HEADERS": '[ "classification", "center_classification_date", "report_date", "postal_code", "termination_date",\n  "recall_initiation_date", "recall_number", "city", "event_id", "distribution_pattern",\n  "recalling_firm", "voluntary_mandated", "state", "reason_for_recall", "initial_firm_notification",\n  "status", "product_type", "country", "product_description", "code_info",\n  "address_1", "address_2", "product_quantity", "more_code_info" ]',
            "RECORD_PATH": "",
            "META": '[ "status", "city", "state", "country", "classification",\n  "openfda", "product_type", "event_id", "recalling_firm", "address_1",\n  "address_2", "postal_code", "voluntary_mandated", "initial_firm_notification", "distribution_pattern",\n  "recall_number", "product_description", "product_quantity", "reason_for_recall", "recall_initiation_date",\n  "center_classification_date", "report_date", "code_info", "more_code_info", "termination_date" ]',
        },
        container_resources={
            "memory": {"request": "32Gi"},
            "cpu": {"request": "2"},
            "ephemeral-storage": {"request": "10Gi"},
        },
    )

    # Task to load CSV data to a BigQuery table
    load_to_bq = gcs_to_bigquery.GCSToBigQueryOperator(
        task_id="load_to_bq",
        bucket="{{ var.value.composer_bucket }}",
        source_objects=["data/fda_food/food_enforcement/files/data_output.csv"],
        source_format="CSV",
        destination_project_dataset_table="{{ var.json.fda_food.food_enforcement_destination_table }}",
        skip_leading_rows=1,
        allow_quoted_newlines=True,
        write_disposition="WRITE_TRUNCATE",
        schema_fields=[
            {
                "name": "classification",
                "type": "STRING",
                "description": "Numerical designation (I, II, or III) that is assigned by FDA to a particular product recall that indicates the relative degree of health hazard. Class I = Dangerous or defective products that predictably could cause serious health problems or death. Examples include: food found to contain botulinum toxin, food with undeclared allergens, a label mix-up on a lifesaving drug, or a defective artificial heart valve. Class II = Products that might cause a temporary health problem, or pose only a slight threat of a serious nature. Example: a drug that is under-strength but that is not used to treat life-threatening situations. Class III = Products that are unlikely to cause any adverse health reaction, but that violate FDA labeling or manufacturing laws. Examples include: a minor container defect and lack of English labeling in a retail food.",
                "mode": "NULLABLE",
            },
            {
                "name": "center_classification_date",
                "type": "DATE",
                "description": "",
                "mode": "NULLABLE",
            },
            {
                "name": "report_date",
                "type": "DATE",
                "description": "Date that the FDA issued the enforcement report for the product recall.",
                "mode": "NULLABLE",
            },
            {
                "name": "postal_code",
                "type": "STRING",
                "description": "",
                "mode": "NULLABLE",
            },
            {
                "name": "termination_date",
                "type": "DATE",
                "description": "",
                "mode": "NULLABLE",
            },
            {
                "name": "recall_initiation_date",
                "type": "DATE",
                "description": "Date that the firm first began notifying the public or their consignees of the recall.",
                "mode": "NULLABLE",
            },
            {
                "name": "recall_number",
                "type": "STRING",
                "description": "A numerical designation assigned by FDA to a specific recall event used for tracking purposes.",
                "mode": "NULLABLE",
            },
            {
                "name": "city",
                "type": "STRING",
                "description": "The city in which the recalling firm is located.",
                "mode": "NULLABLE",
            },
            {
                "name": "event_id",
                "type": "INTEGER",
                "description": "A numerical designation assigned by FDA to a specific recall event used for tracking purposes.",
                "mode": "NULLABLE",
            },
            {
                "name": "distribution_pattern",
                "type": "STRING",
                "description": "General area of initial distribution such as, “Distributors in 6 states: NY, VA, TX, GA, FL and MA; the Virgin Islands; Canada and Japan”. The term “nationwide” is defined to mean the fifty states or a significant portion. Note that subsequent distribution by the consignees to other parties may not be included.",
                "mode": "NULLABLE",
            },
            {
                "name": "recalling_firm",
                "type": "STRING",
                "description": "The firm that initiates a recall or, in the case of an FDA requested recall or FDA mandated recall, the firm that has primary responsibility for the manufacture and (or) marketing of the product to be recalled.",
                "mode": "NULLABLE",
            },
            {
                "name": "voluntary_mandated",
                "type": "STRING",
                "description": "Describes who initiated the recall. Recalls are almost always voluntary, meaning initiated by a firm. A recall is deemed voluntary when the firm voluntarily removes or corrects marketed products or the FDA requests the marketed products be removed or corrected. A recall is mandated when the firm was ordered by the FDA to remove or correct the marketed products, under section 518(e) of the FD&C Act, National Childhood Vaccine Injury Act of 1986, 21 CFR 1271.440, Infant Formula Act of 1980 and its 1986 amendments, or the Food Safety Modernization Act (FSMA).",
                "mode": "NULLABLE",
            },
            {
                "name": "state",
                "type": "STRING",
                "description": "The U.S. state in which the recalling firm is located.",
                "mode": "NULLABLE",
            },
            {
                "name": "reason_for_recall",
                "type": "STRING",
                "description": "Information describing how the product is defective and violates the FD&C Act or related statutes.",
                "mode": "NULLABLE",
            },
            {
                "name": "initial_firm_notification",
                "type": "STRING",
                "description": "The method(s) by which the firm initially notified the public or their consignees of a recall. A consignee is a person or firm named in a bill of lading to whom or to whose order the product has or will be delivered.",
                "mode": "NULLABLE",
            },
            {
                "name": "status",
                "type": "STRING",
                "description": "On-Going = A recall which is currently in progress.  Completed = The recall action reaches the point at which the firm has actually retrieved and impounded all outstanding product that could reasonably be expected to be recovered, or has completed all product corrections. Terminated = FDA has determined that all reasonable efforts have been made to remove or correct the violative product in accordance with the recall strategy, and proper disposition has been made according to the degree of hazard. Pending = Actions that have been determined to be recalls, but that remain in the process of being classified.",
                "mode": "NULLABLE",
            },
            {
                "name": "product_type",
                "type": "STRING",
                "description": "",
                "mode": "NULLABLE",
            },
            {
                "name": "country",
                "type": "STRING",
                "description": "The country in which the recalling firm is located.",
                "mode": "NULLABLE",
            },
            {
                "name": "product_description",
                "type": "STRING",
                "description": "Brief description of the product being recalled.",
                "mode": "NULLABLE",
            },
            {
                "name": "code_info",
                "type": "STRING",
                "description": "A list of all lot and/or serial numbers, product numbers, packer or manufacturer numbers, sell or use by dates, etc., which appear on the product or its labeling.",
                "mode": "NULLABLE",
            },
            {
                "name": "address_1",
                "type": "STRING",
                "description": "",
                "mode": "NULLABLE",
            },
            {
                "name": "address_2",
                "type": "STRING",
                "description": "",
                "mode": "NULLABLE",
            },
            {
                "name": "product_quantity",
                "type": "STRING",
                "description": "The amount of defective product subject to recall.",
                "mode": "NULLABLE",
            },
            {
                "name": "more_code_info",
                "type": "STRING",
                "description": "",
                "mode": "NULLABLE",
            },
        ],
    )

    transform_csv >> load_to_bq
