from ruamel.yaml import YAML
from datetime import datetime

class MetadataUpdater:
    def __init__(self, filepath):
        """
        Initializes the class with the path where the YAML file will be saved.
        """
        self.filepath = filepath
        self.yaml = YAML()
        self.yaml.indent(mapping=2, sequence=4, offset=2)  # Optional: customize YAML formatting

    def update_yml(self, variable, resources, additional_info):
        """
        Updates or creates the YAML file with the provided details.
        Automatically updates the date.
        
        Parameters:
        - variable: dict with keys 'name', 'subsector', 'longname', and 'units'
        - resources: dict with keys 'url' and 'descrip'
        - additional_info: dict with key 'assumptions'
        """
        data = {
            'latest update date': datetime.now().strftime('%Y-%m-%d'),  # Automatically set the current date
            'variable': {
                'name': variable.get('name', ''),
                'subsector': variable.get('subsector', ''),
                'longname': variable.get('longname', ''),
                'units': variable.get('units', '')
            },
            'resources': {
                'url': resources.get('url', ''),
                'descrip': resources.get('descrip', '')
            },
            'additional_information': {
                'assumptions': additional_info.get('assumptions', '')
            }
        }

        # Write or update the YAML file with the desired order
        with open(self.filepath, 'w') as file:
            self.yaml.dump(data, file)

        print(f"YAML file updated successfully at {self.filepath}")
