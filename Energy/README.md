# Energy Data Updates
## Update Oct 10, 2024 (Juan Antonio Robledo)

The following data inputs were updated with the information provided by Sonya (Iran Selected Energy data). The fuel price data was selected based on the 2021/22 fuel price information from the source, and each price was converted to the appropriate units for use in both the historical and projected datasets for Iran in the energy models.

### List of Updated Fuel Prices:

- **cost_enfu_fuel_diesel_usd_per_m3:**
  The cost of diesel in USD per cubic meter was updated using the value 0.0036 USD per liter, sourced from diesel prices for power plants (row 6 in the source data). The value was chosen based on the most stable entry, considering the variation in the range provided.

- **cost_enfu_fuel_electricity_usd_per_mmbtu:**
  The cost of electricity in USD per million BTU was updated using the value 0.007932 USD per kilowatt-hour, sourced from the electricity price (row 0 in the source data). This value was directly taken as it reflects the latest price available.

- **cost_enfu_fuel_gasoline_usd_per_m3:**
  The cost of regular gasoline in USD per cubic meter was updated using the value 0.041141 USD per liter, sourced from the subsidized gasoline price (row 1 in the source data). This was chosen over the free-market price to reflect the subsidized rate applicable to most consumers.

- **cost_enfu_fuel_hydrocarbon_gas_liquids_usd_per_mmbtu:**
  The cost of liquefied gas in USD per million BTU was updated using the value 0.145793 USD per liter, as directly sourced from the liquefied gas price (row 10 in the source data). This value represents the latest available price.

- **cost_enfu_fuel_kerosene_usd_per_m3:**
  The cost of kerosene in USD per cubic meter was updated using the value 0.004114 USD per liter, sourced from kerosene prices for power plants (row 5 in the source data).

- **cost_enfu_fuel_natural_gas_usd_per_mmbtu:**
  The cost of natural gas in USD per million BTU was updated using the value 0.003764 USD per kilogram, as sourced from the natural gas price (row 11 in the source data).

The data for these fuels was updated in both the **historical** and **projected** datasets located in the respective folder structure under `input_to_sisepuede`. The updates were specifically applied to the Iranian data (iso_code3 = 'IRN').
