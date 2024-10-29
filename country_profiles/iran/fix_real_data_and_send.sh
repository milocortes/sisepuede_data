#!/bin/bash
#python fix_pij_other.py
cp backup_real_data/real_data.csv .
python fix_gdp_pop.py
python add_frac_inen.py
python add_trns_missing_var.py

cp real_data.csv ssp_iran/opt/ssp_input_data
