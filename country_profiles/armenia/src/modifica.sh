#!/bin/bash
python3 /opt/build_real_data.py armenia
python3 fix_pij_other.py
python3 actualiza_time_period.py 36
python3 /opt/build_ssp_input_data.py
cp /opt/sisepuede/ref/ingestion/calibrated/armenia/model_input_variables_armenia_af_calibrated.xlsx /opt/sisepuede/ref/ingestion/calibrated/armenia/model_input_variables_armenia_af_calibrated_backup.xlsx
python3 change_pij.py
python3 update_template_exec_time.py
python3 actualiza_time_period.py 46
#bash /opt/ejecuta-sisepuede.sh --regions armenia --keys-strategy 1015,5009 --keys-design 0 --keys-future 0 --database-type csv --save-inputs --exclude-fuel-production
bash /opt/ejecuta-sisepuede.sh --regions armenia --keys-strategy 1015,5009 --keys-design 0 --keys-future 0 --database-type csv --save-inputs 
rm /opt/SSP_RESULTS/*
find /opt/sisepuede/out/ -type f -name "*.csv" -exec mv  "{}" /opt/SSP_RESULTS \;
python3 /opt/merge_ssp_input_output_data.py

