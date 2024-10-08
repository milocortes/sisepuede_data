# sisepuede_data

### How to Update Livestock Data

1. Ensure that you have the most up-to-date CSV file with FAO data in the [AFOLU/pop_lvst_raw_data](AFOLU/pop_lvst_raw_data) directory.
2. Make sure the file is named `FAOSTAT_livestock_data`.
3. Make sure your file has a column with the ISO3 country codes. This can be set when downloading the csv from the FAOSTAT website.
4. Run the [initial_lvst_preprocessing.py](data_processing_scripts_AFOLU/initial_lvst_preprocessing.py) script to update all initial livestock data.
5. You can check the [initial_lvst_preprocessing.ipynb](data_processing_scripts_AFOLU/initial_lvst_preprocessing.ipynb) notebook to debug the preprocessing code or test new features.

#### TODO:
- Enable automatic downloading of livestock data via the API.
- The projected data method could be improved with a more robust imputation technique.
- Eliminate the redundant files in the initial lvst data folders.

#### Comments:
- The groupby methods were elimineted since the crosswalk mapping does not match several FAO categories into a single SISEPUEDE category.

### How to Update Crop Yield Data

1. Ensure that you have the most up-to-date CSV file with FAO data in the [AFOLU/yf_agrc_raw_data](AFOLU/yf_agrc_raw_data) directory.
2. Make sure the file is named `FAOSTAT_crop_data`.
3. Run the [yf_crops_preprocessing.py](AFOLU_data_preprocessing_scripts/yf_crops_preprocessing.py) script to update all initial livestock data.
4. You can check the [yf_crops_preprocessing.ipynb](AFOLU_data_preprocessing_scripts/yf_crops_preprocessing.ipynb) notebook to debug the preprocessing code or test new features.