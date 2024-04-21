import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

######################### Dynamicaly read files on subfolder "Bank_Monthly_Movements" #########################

# Folder structure this code expects:
#
# Current Directory
# └── Bank_Monthly_Movements/
# │   ├── Movements.xls
# │   │
# │   └── ...

# Construct path
current_directory = os.getcwd()
Bank_Monthly_Movements_path = os.path.join(current_directory, 'Bank_Monthly_Movements')
Movements_path = os.path.join(Bank_Monthly_Movements_path, 'Movements.xls')

# Read file into dataframe
Movements_df = pd.read_excel(Movements_path, header=5, sheet_name='Movimientos')

# Cast the numerical values to floats
Movements_df['IMPORTE (€)'] = Movements_df['IMPORTE (€)'].astype(float)
Movements_df['SALDO (€)'] = Movements_df['SALDO (€)'].astype(float)




# Our excel sheet may contain several months (up to 12) of movements, thus is we want to visualize our monthly spendings
# we may reuse the code written but only if we first split the dataframe into one per month


# 1) Define funciton that checks the date string on each row and returns an indexing series (array like object of bools) 
# depending on if there's a match for the month provided or not.
# def Index_by_month(month, df):

# 2) Create a dataframe for each month with each indexing series

# 3) Iterate through them and calculate expenses for each of them

# 4) Create a graph over time for each expense, don't normalize and use something similar to fill()