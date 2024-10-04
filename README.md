# sisepuede_data

### How to update livestock data
1. Make sure you have the most up to date csv file with FAO data inside [AFOLU/pop_lvst_data_raw](AFOLU/pop_lvst_data_raw).
2. Make sure the name of the file is `FAOSTAT_data`
2. Run the [initial_lvst_processing](data_processing_scripts.AFOLU/intial_lvst_processing.py) script so all intial livestock data is updated.

#### TODO:
- Being able to download the livestock data automatically through the API.
- The HTTP request for the m49 countries JSON is not working for me (Juan Antonio).