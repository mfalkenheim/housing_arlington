import pandas as pd
import numpy as np
from urllib import request      
import gzip
import pickle
from utils import load_housing_data


#improvement_exterior = load_housing_data("RealEstate/ImprovementExterior.txt")
#improvement_dwelling = load_housing_data("RealEstate/ImprovementDwelling.txt")
#improvement_interior = load_housing_data("RealEstate/ImprovementExterior.txt")
#outbuilding = load_housing_data("RealEstate/Outbuilding.txt")
#porches = load_housing_data("RealEstate/ImprovementPorch.txt")
permits = load_housing_data("Permit/Permit.txt.gz")
permits = permits[permits['AppliedDate'].notna()]
years = permits['AppliedDate'].str.slice(0, 4).astype(int) >= 2023
months = permits['AppliedDate'].str.slice(5, 7).astype(int) >= 7
#days = permits['AppliedDate'].str.slice(8, 10).astype(int)
recent = years & months
cnew = permits['PermitTypeAliasName'] == 'Commercial New'
demo = permits['PermitTypeAliasName'] == 'Demolition'
goodtype = cnew + demo
possible_mm_permits = permits[recent * goodtype][['PermitDescriptionText', \
    'AppliedDate','StreetAddressText', 'ContractorName', 'PermitTypeAliasName']]
for row in possible_mm_permits.iterrows():
  print(row)
"""
sales_history = load_housing_data("SalesHistory.txt")
assessments = load_housing_data("RealEstate/Assessment.txt.gz")
development_projects = load_housing_data("HousingBuilding/DevelopmentProject.txt")
permits = load_housing_data("Housing/Building/Permit.txt.gz")
"""