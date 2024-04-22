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
def Index_by_month(Timestamp, month, year):
    
    """
    This function takes a Timestamp and check wether it matches a certain month and year.
    It is meant to be used with the 'apply()' method in pandas to generate and indexing mask
    that extracts data for only one month. 

    Parameters
    ----------
    Timestamp : ??
        The element on each row

    month : int

    year :  int

    Returns 
    -------
    Bool
        True for a matching element, False if not.    
    """

    # Check if the Timestamp type variable has a matching month and year
    if (Timestamp.month == month and Timestamp.year == year):
        return True
    
    else:
        return False


# Get the column series storing dates for each movement
Dates_df = Movements_df['F. VALOR'] 

# Find how many months/years we need to split the df into
First_month = Dates_df.tolist()[-1].month
First_year = Dates_df.tolist()[-1].year
Last_month = Dates_df.tolist()[0].month
Last_year = Dates_df.tolist()[0].year

# Construct a list of dates to iterate through, with structure : [int month, int year ]
Dates = []
if (Last_year > First_year):
    for year in range(First_year, Last_year+1):

        if (year == First_year):
            for month in range(First_month, 12+1):
                Dates.append([month, year])

        elif (year == Last_year):
            for month in range(1, Last_month+1):
                Dates.append([month, year])

        else:
            for month in range(1, 12+1):
                Dates.append([month, year])

elif (Last_year == First_year):
    for month in range(First_month, Last_month+1):
        Dates.append([month, First_year])

# Iterate through them and store them on a list
Months = []
for date in Dates:
    month, year = date[0], date[1]

    # Apply the funciton to each element and pass month as an additional argument
    Indexing_df = Dates_df.apply(Index_by_month, args=(month, year))

    # Create a dataframe for each month with each indexing series
    Months.append(Movements_df[Indexing_df])

    
# Iterate through them and calculate expenses for each of them


# 4) Create a graph over time for each expense, don't normalize and use something similar to fill()

