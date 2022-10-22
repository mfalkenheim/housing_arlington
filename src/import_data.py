import pandas as pd
import numpy as np
from urllib import request      
import gzip
import pickle


url = "https://download.data.arlingtonva.us/RealEstate/ImprovementExterior.txt"
improvement_exterior = pd.read_csv(request.urlopen(url), header=0, sep='|')
improvement_exterior.to_pickle("./data/improvement_exterior.pkl")
url = "https://download.data.arlingtonva.us/RealEstate/ImprovementDwelling.txt"
improvement_dwelling = pd.read_csv(request.urlopen(url), header=0, sep='|')
improvement_dwelling.to_pickle("./data/improvement_dwelling.pkl")
url = "https://download.data.arlingtonva.us/RealEstate/ImprovementInterior.txt"
improvement_interior = pd.read_csv(request.urlopen(url), header=0, sep='|')
improvement_interior.to_pickle("./data/improvement_interior.pkl")
url = "https://download.data.arlingtonva.us/RealEstate/Outbuilding.txt"
outbuilding = pd.read_csv(request.urlopen(url), header=0, sep='|')
outbuilding.to_pickle("./data/outbuilding.pkl")
url = "https://download.data.arlingtonva.us/RealEstate/ImprovementPorch.txt"
porches = pd.read_csv(request.urlopen(url), header=0, sep='|')
porches.to_pickle("./data/porches.pkl")
url = "https://download.data.arlingtonva.us/RealEstate/PropertyAddress.txt"
property_address = pd.read_csv(request.urlopen(url), header=0, sep='|')
property_address.to_pickle("./data/property_address.pkl")
url = "https://download.data.arlingtonva.us/RealEstate/SalesHistory.txt"
sales_history = pd.read_csv(request.urlopen(url), header=0, sep='|')
sales_history.to_pickle("./data/sales_history.pkl")
url = "https://download.data.arlingtonva.us/RealEstate/Assessment.txt.gz"
assessments = pd.read_csv(request.urlopen(url), compression='gzip', header=0, sep='|')
assessments.to_pickle("./data/assessments.pkl")
url = "https://download.data.arlingtonva.us/HousingBuilding/DevelopmentProject.txt"
development_projects = pd.read_csv(request.urlopen(url), header=0, sep='|')
development_projects.to_pickle("./data/development_projects.pkl")
url = "https://download.data.arlingtonva.us/Permit/Permit.txt.gz"
permits = pd.read_csv(request.urlopen(url), compression = 'gzip', header=0, sep='|')
permits.to_pickle("./data/permits.pkl")