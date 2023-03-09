
'''
+++++++++++++++++++++++++++++++++++++++

---- CORESPONDENCIAS ---

+++++++++++++++++++++++++++++++++++++++
'''
fuels_sisepuede = ['coal', 'coke', 'diesel', 'electricity', 'gas furnace', 'gas petroleum liquid', 'gasoline', 'hydrogen', 'kerosene', 'natural gas', 'oil', 'solar', 'solid biomass']
fuels_iea = ['Coal and coal products (PJ)', 'Combustible renewables and waste (PJ)', 'Electricity (PJ)', 'Gas (PJ)', 'Heat (PJ)', 'Oil and oil products (PJ)', 'Other sources (PJ)']

## Combustible renewables and waste (% of total energy) 
# https://databank.worldbank.org/metadataglossary/africa-development-indicators/series/EG.USE.CRNW.ZS
# Definition:
# Combustible renewables and waste comprise solid biomass, liquid biomass, biogas, industrial waste, and municipal waste, measured as a percentage of total energy use.


fuels_correspondence = {
        'coal' : (0.90, 'Coal and coal products (PJ)'),
        'coke' : (0.10, 'Coal and coal products (PJ)'),  
        'diesel' : (0.15, 'Oil and oil products (PJ)'),  
        'electricity' : (1.0, 'Electricity (PJ)'),
        'furnace_gas' : (1.0, 'Heat (PJ)'), ## gas_furnace ----> furnace_gas
        'hydrocarbon_gas_liquids' : None, ## gas_petroleum_liquid ----> hydrocarbon_gas_liquids
        'gasoline' : (0.15, 'Oil and oil products (PJ)'),  
        'hydrogen' : None,  
        'kerosene' : None,  
        'natural_gas' : (1.0, 'Gas (PJ)'), 
        'oil' : (0.7, 'Oil and oil products (PJ)'), 
        'solar' : (1.0, 'Other sources (PJ)'), 
        #'solid_biomass': (1.0, 'Combustible renewables and waste (PJ)') ## Ya no aparece en la nueva base de datos. Cambiamos por 'Biofuels and waste (PJ)'
        'solid_biomass': (1.0, 'Biofuels and waste (PJ)')
        }

industries_sisepuede = ['recycled_rubber_and_leather', 'recycled_textiles', 'electronics', 'plastic', 'chemicals', 'cement',
'glass', 'recycled_metals', 'other_product_manufacturing', 'agriculture_and_livestock', 'textiles', 'rubber_and_leather',
'recycled_plastic', 'metals', 'recycled_wood', 'recycled_glass', 'recycled_paper', 'lime_and_carbonite', 'paper']

industries_iea = ['Agriculture, forestry and fishing [ISIC 01-03]',
'Basic metals [ISIC 24]',
'Chemicals and chemical products [ISIC 20-21]',
'Construction [ISIC 41-43]',
'Ferrous metals [ISIC 2410+2431]',
'Food and tobacco [ISIC 10-12]',
'Machinery [ISIC 25-28]',
'Manufacturing [ISIC 10-18, 20-32]',
'Memo: Coke and refined petroleum products [ISIC 19]',
'Mining [ISIC 05-09]',
'Non-ferrous metals [ISIC 2420+2432]',
'Non-metallic minerals [ISIC 23]',
'Non-specified manufacturing',
'Of which: cement',
'Other manufacturing [ISIC 31-32]',
'Paper pulp and printing [ISIC 17-18]',
'Rubber and plastic [ISIC 22]',
'Textiles and leather [ISIC 13-15]',
'Transport equipment [ISIC 29-30]',
'Wood and wood products [ISIC 16]']

industries_iea = [
'Construction [ISIC 41-43]',
'Ferrous metals [ISIC 2410+2431]',
'Food and tobacco [ISIC 10-12]',
'Manufacturing [ISIC 10-18, 20-32]',
'Memo: Coke and refined petroleum products [ISIC 19]',
'Mining [ISIC 05-09]',
'Non-specified manufacturing',
'Transport equipment [ISIC 29-30]']

"""
industries_correspondence = {
                'electronics' : (1.0, 'Machinery [ISIC 25-28]'), 
                'plastic' : (1.0, 'Rubber and plastic [ISIC 22]'), 
                'chemicals' : (1.0, 'Chemicals and chemical products [ISIC 20-21]'), 
                'cement' : (1.0, 'Of which: cement'),
                'glass' : (1.0, 'Non-metallic minerals [ISIC 23]'), 
                'other_product_manufacturing' : (1.0, 'Other manufacturing [ISIC 31-32]'), 
                'agriculture_and_livestock' : (1.0, 'Agriculture, forestry and fishing [ISIC 01-03]'), 
                'textiles' : (0.5, 'Textiles and leather [ISIC 13-15]'), 
                'rubber_and_leather' : (0.5, 'Textiles and leather [ISIC 13-15]'), 
                'metals' : (1.0, 'Basic metals [ISIC 24]'),  
                'lime_and_carbonite' : (1.0, 'Non-ferrous metals [ISIC 2420+2432]'), 
                'paper' : (1.0, 'Paper pulp and printing [ISIC 17-18]'),
                'recycled_wood' : (1.0, 'Wood and wood products [ISIC 16]') 
                }
"""
industries_correspondence = {
  'electronics' : (0.5, 'Machinery [ISIC 25-28]'), #Electronics is ISIC 26 and 27, so let's say half of 25-28
  'plastic' : (0.5, 'Rubber and plastic [ISIC 22]'), # SEE BELOW
  'chemicals' : (1.0, 'Chemicals and chemical products [ISIC 20-21]'), #OK
  'cement' : (0.9, 'Non-metallic minerals [ISIC 23]'), #FIXED
  'glass' : (0.05, 'Non-metallic minerals [ISIC 23]'), #FIXED
  'other_product_manufacturing' : (1.0, 'Other manufacturing [ISIC 31-32]'), #OK
  'agriculture_and_livestock' : (1.0, 'Agriculture forestry and fishing [ISIC 01-03]'), #OK
  'textiles' : (0.5, 'Textiles and leather [ISIC 13-15]'), #SEE BELOW
  'rubber_and_leather' : (0.5, 'Textiles and leather [ISIC 13-15]'), #+ AND 0.5  'Rubber and plastic [ISIC 22]'
  'metals' : (1.0, 'Basic metals [ISIC 24]'), #OK
  'lime_and_carbonite' : (0.05, 'Non-metallic minerals [ISIC 23]'), #FIXED
  'paper' : (1.0, 'Paper pulp and printing [ISIC 17-18]'),
  'recycled_wood' : (1.0, 'Wood and wood products [ISIC 16]') #I propose we leave this out entirely, unless we are doing all recyclables
}

industries_correspondence_recycled = {
                'rubber_and_leather' : 'recycled_rubber_and_leather', 
                'textiles' : 'recycled_textiles',
                'metals' : 'recycled_metals',
                'plastic' : 'recycled_plastic',
                'glass' : 'recycled_glass', 
                'paper' : 'recycled_paper' 
                }
