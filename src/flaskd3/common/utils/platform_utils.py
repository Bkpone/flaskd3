import os
import csv
import json


SEED_LOCATION = "resources/seeds"


def read_from_seed(domain, resource, schema):
    home_dir = os.environ.get("HOME_DIR", os.getcwd())
    seed_file_path = os.path.join(home_dir, SEED_LOCATION, domain, resource + ".json")
    parsed_values = list()
    with open(seed_file_path) as seed_file:
        entries = json.load(seed_file)
        for entry in entries:
            parsed_value = schema(unknown="EXCLUDE").load(entry) if schema else entry
            parsed_values.append(parsed_value)
    return parsed_values
