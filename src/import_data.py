import pandas as pd
import numpy as np
from urllib import request      
import gzip


url = "https://download.data.arlingtonva.us/RealEstate/ImprovementExterior.txt"
improvement_exterior = pd.read_csv(request.urlopen(url), header=0, sep='|')
url = "https://download.data.arlingtonva.us/RealEstate/ImprovementDwelling.txt"
improvement_dwelling = pd.read_csv(request.urlopen(url), header=0, sep='|')
url = "https://download.data.arlingtonva.us/RealEstate/ImprovementInterior.txt"
improvement_interior = pd.read_csv(request.urlopen(url), header=0, sep='|')
url = "https://download.data.arlingtonva.us/RealEstate/Outbuilding.txt"
outbuilding = pd.read_csv(request.urlopen(url), header=0, sep='|')
url = "https://download.data.arlingtonva.us/RealEstate/ImprovementPorch.txt"
porches = pd.read_csv(request.urlopen(url), header=0, sep='|')
url = "https://download.data.arlingtonva.us/RealEstate/PropertyAddress.txt"
property_address = pd.read_csv(request.urlopen(url), header=0, sep='|')
print(property_address.head)
url = "https://download.data.arlingtonva.us/RealEstate/SalesHistory.txt"
sales_history = pd.read_csv(request.urlopen(url), header=0, sep='|')
print(sales_history.head)
url = "https://download.data.arlingtonva.us/RealEstate/Assessment.txt.gz"
assessments = pd.read_csv(request.urlopen(url), compression='gzip', header=0, sep='|')
print(assessments.head)
url = "https://download.data.arlingtonva.us/HousingBuilding/DevelopmentProject.txt"
development_projects = pd.read_csv(request.urlopen(url), header=0, sep='|')
url = "https://download.data.arlingtonva.us/Permit/Permit.txt.gz"
permits = pd.read_csv(request.urlopen(url), compression = 'gzip', header=0, sep='|')
