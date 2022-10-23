import pandas as pd
import numpy as np
from urllib import request      
import gzip
import pickle
from utils import load_housing_data


improvement_exterior = load_housing_data("RealEstate/ImprovementExterior.txt")
improvement_dwelling = load_housing_data("RealEstate/ImprovementDwelling.txt")
improvement_interior = load_housing_data("RealEstate/ImprovementExterior.txt")
outbuilding = load_housing_data("RealEstate/Outbuilding.txt")
porches = load_housing_data("RealEstate/ImprovementPorch.txt")

"""
sales_history = load_housing_data("SalesHistory.txt")
assessments = load_housing_data("RealEstate/Assessment.txt.gz")
development_projects = load_housing_data("HousingBuilding/DevelopmentProject.txt")
permits = load_housing_data("Housing/Building/Permit.txt.gz")
"""