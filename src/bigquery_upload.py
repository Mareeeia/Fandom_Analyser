import json

from google.cloud import bigquery

from src.params.folder_params import *


def upload_json_to_table(fandom):
    client = bigquery.Client()
    dataset_id = 'works'
    table_id = 'works_table'
    filename = ROOT_DIR + FILES_ROOT + fandom + PROCESSED_WORKS

    dataset_ref = client.dataset(dataset_id)
    table_ref = dataset_ref.table(table_id)
    job_config = bigquery.LoadJobConfig()
    job_config.source_format = bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
    job_config.autodetect = True

    with open(filename, "rb") as source_file:
        json_content = json.load(source_file)
        with open(ROOT_DIR + FILES_ROOT + fandom + PROCESSED_TEMP, 'w') as file:
            make_format(json_content, file, fandom)
        with open(ROOT_DIR + FILES_ROOT + fandom + PROCESSED_TEMP, "rb") as array_file:
            job = client.load_table_from_file(
                array_file,
                table_ref,
                location="europe-west6",  # Must match the destination dataset location.
                job_config=job_config,
            )  # API request

    job.result()  # Waits for table load to complete.

    print("Loaded {} rows into {}:{}.".format(job.output_rows, dataset_id, table_id))



def make_format(dict_json: dict, file, fandom: str):
    """Produce line-delimited json for the BigQuery requirements"""
    array: list = []
    for work_key in dict_json.keys():
        new_work = dict_json[work_key]
        new_work["id"] = work_key
        new_work["fandom"] = fandom
        json.dump(new_work, file)
        file.write('\n')
    return array
