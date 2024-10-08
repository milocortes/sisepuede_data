# sisepuede_data

### How to Update Livestock Data

1. Ensure that you have the most up-to-date CSV file with FAO data in the [AFOLU/pop_lvst_data_raw](AFOLU/pop_lvst_data_raw) directory.
2. Make sure the file is named `FAOSTAT_livestock_data`.
3. Run the [initial_lvst_preprocessing.py](data_processing_scripts_AFOLU/initial_lvst_preprocessing.py) script to update all initial livestock data.
4. You can check the [initial_lvst_preprocessing.ipynb](data_processing_scripts_AFOLU/initial_lvst_preprocessing.ipynb) notebook to debug the preprocessing code or test new features.

#### TODO:
- Enable automatic downloading of livestock data via the API.
- The HTTP request for the m49 countries JSON isn't working for me (Juan Antonio), so I downloaded the file manually.
- The projected data method could be improved with a more robust imputation technique.
- Eliminate the redundant files in the initial lvst data folders.