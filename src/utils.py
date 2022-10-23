import pandas as pd
from urllib import request 

def load_housing_data(path):
    url = "https://download.data.arlingtonva.us/" + path
    if path[-3:] == ".gz":
        return(pd.read_csv(request.urlopen(url), compression = 'gzip', header=0, sep='|'))
    else:
        return(pd.read_csv(request.urlopen(url), header=0, sep='|'))
        