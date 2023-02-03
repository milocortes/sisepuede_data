road_heavy_freight = ['frac_trns_fuelmix_road_heavy_freight_biofuels',
 'frac_trns_fuelmix_road_heavy_freight_diesel',
 'frac_trns_fuelmix_road_heavy_freight_electricity',
 'frac_trns_fuelmix_road_heavy_freight_gasoline',
 'frac_trns_fuelmix_road_heavy_freight_hydrogen',
 'frac_trns_fuelmix_road_heavy_freight_natural_gas']

road_heavy_regional = [ 'frac_trns_fuelmix_road_heavy_regional_biofuels',
 'frac_trns_fuelmix_road_heavy_regional_diesel',
 'frac_trns_fuelmix_road_heavy_regional_electricity',
 'frac_trns_fuelmix_road_heavy_regional_gasoline',
 'frac_trns_fuelmix_road_heavy_regional_hydrogen',
 'frac_trns_fuelmix_road_heavy_regional_natural_gas']

correspondencias_regional_to_freight = {regional:freight for regional, freight in zip(road_heavy_regional, road_heavy_freight)}

correspondencias_freight_to_regional = {freight:regional for regional, freight in zip(road_heavy_regional, road_heavy_freight)}