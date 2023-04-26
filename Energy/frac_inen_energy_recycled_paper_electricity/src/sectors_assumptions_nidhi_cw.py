
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


#Cross Walk with IEA data updated 4/25
industries_correspondence = {
  
  #The following categories have a 1:1 correspondence between IEA and SSP
  #However, we need to discuss two things with James:
  #(1) should we only be allocating to SSP mining the fraction of IEA mining that is non-fuels related?
  #(2) is agriculture_and_livestock behaving ok given that it is treated differently in the model
  'agriculture_and_livestock' : [(1.0, 'Agriculture forestry and fishing [ISIC 01-03]')], #OK
  'metals' : [(1.0, 'Basic metals [ISIC 24]')], #OK
  'chemicals' : [(1.0, 'Chemicals and chemical products [ISIC 20-21]')], #OK
  'paper' : [(1.0, 'Paper pulp and printing [ISIC 17-18]')],
  'mining': [(1.0, 'Mining [ISIC 05-09]')] ,#added 4/25 -- CHECK WITH JAMES should it be 100% or part?
  

  #In the following rows, a single IEA category is split across multiple SSP categories
  #Here, 'Non-metallic minerals [ISIC 23]' covers cement, glass, and lime/carbonite.
  #the 75% of cement is based on the "Of Which" data for LAC in IEA
  #The remaining 25% is split equally across glass and lime/carbonite
  'cement' : [(0.75, 'Non-metallic minerals [ISIC 23]')], #updated 4/25 from 0.9
  'glass' : [(0.125, 'Non-metallic minerals [ISIC 23]')], #updated 4/25 from 0.05
  'lime_and_carbonite' : [(0.125, 'Non-metallic minerals [ISIC 23]')], #updated 4/25 from 0.05
  
  
  #In the following rows, there's a more complex split between SSP and IEA, as explained
  
  #IEA's Machinery [ISIC 25-28]' includes electronics [ISIC 26 and 27]
  #in the absence of better information, we assume half of energy demands in Machinery [ISIC 25-28]
  #relate to electronics, and the other half are put in SSP's other product manufacturing
  'electronics' : [(0.5, 'Machinery [ISIC 25-28]')],


  'plastic' : [(0.5, 'Rubber and plastic [ISIC 22]')], # SEE BELOW
  'textiles' : [(0.5, 'Textiles and leather [ISIC 13-15]')], #SEE BELOW

  #SSP's Other product manufacturing includes emissions from any IEA category that doesn't have
  #a mapping to an SSP category, or only has a partial mapping, like Machinery [ISIC 25-28]
  'other_product_manufacturing' : [(1.0, 'Other manufacturing [ISIC 31-32]'), #OK
                                   (1.0, 'Construction [ISIC 41-43]'), #added 4/25
                                   (1.0, 'Food and tobacco [ISIC 10-12]'), #added 4/25
                                   (1.0, 'Transport equipment [ISIC 29-30]'), #added 4/25
                                   (1.0, 'Wood and wood products [ISIC 16]'), #added 4/25
                                   (1.0, 'Non-specified manufacturing'), #added 4/25
                                   (0.5, 'Machinery [ISIC 25-28]')], #added 4/25, other half of machinery is electronics
  
  #IEA groups (rubber and plastic) together and (textiles and leather) together.
  #SSP separates plastics and textiles but groups (rubber and leather) together
  #To allow for this, we say half of Rubber and plastic [ISIC 22] goes to SSP rubber_and_leather, the other half goes to plastics
  #and half of 'Textiles and leather [ISIC 13-15]' goes to SSP rubber_and_leather and the other half goes to textiles

  'rubber_and_leather' : [(0.5, 'Textiles and leather [ISIC 13-15]'),
                          (0.5, 'Rubber and plastic [ISIC 22]')],
  'wood' : [(1.0, 'Wood and wood products [ISIC 16]')],
  }

industries_correspondence_recycled = {
                'rubber_and_leather' : 'recycled_rubber_and_leather', 
                'textiles' : 'recycled_textiles',
                'metals' : 'recycled_metals',
                'plastic' : 'recycled_plastic',
                'glass' : 'recycled_glass', 
                'paper' : 'recycled_paper' ,
                'wood' : 'recycled_wood'
                }
