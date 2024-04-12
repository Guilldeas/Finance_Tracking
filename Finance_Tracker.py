
'''
Trackear spendings and net worth

Spendings:

	- Savings (0)

	- Eating out Work ("Pago en CAFET. IMDEA NANOCIENCIA MADRID ES" + "Pago en LA ESTACION DE MAJADAHONDMAJADAHONDA ES")

	- Uber to Work ("Taxi y Carsharing")

	- Recreational
		- Eating out ("Cafeterías y restaurantes" + "Supermercados y alimentacion" - "Eating out Work")
		- Bars
		- Bizum ("Transferencia Bizum emitida" - "Transferencia Bizum recibida?")
		- Uber (No se puede diferencias)

	- Living expenses
		- Psychologist (Check wether there's a 210 withdrawal in "Cajeros")
		- Dystopia (Check wether there's a 15 movement in "Transferencia Bizum emitida")
		- ChatGPT ("Pago en CHATGPT SUBSCRIPTION")

    - Untracked
        - "Total" - "Accumulated Spendings"
'''

import os
import pandas as pd


def accumulate_movements (Concept):
    
    # This function looks for movements with a certain type of concept (str) and returns the 
    # accumulated expenses for all movements found.

    # Create a boolean series indicating matches for the subcategory we are interested in
    # Don't ask the user to specify the columns, simply search in both columns
    Indexing_Series_subcat = Movements_df['SUBCATEGORÍA'] == Concept
    Indexing_Series_decrip = Movements_df['DESCRIPCIÓN'] == Concept

    # Then use only the one that contains any instances of the concept 
    if (Indexing_Series_subcat.any()):

        # Trim out any rows that do not contain any instances
        filtered_df = Movements_df[Indexing_Series_subcat]

    elif (Indexing_Series_decrip.any()):
        filtered_df = Movements_df[Indexing_Series_decrip]

    # Return all expenses for the specified instance
    return filtered_df['IMPORTE (€)'].sum()


# Read the .xls file

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
# Casting the 'Amount' column to float
Movements_df['IMPORTE (€)'] = Movements_df['IMPORTE (€)'].astype(float)
Movements_df['SALDO (€)'] = Movements_df['SALDO (€)'].astype(float)

# Find all instances of movements due to Uber rides
Eating_Out_Work = accumulate_movements('Pago en CAFET. IMDEA NANOCIENCIA MADRID ES') + accumulate_movements('Pago en LA ESTACION DE MAJADAHONDMAJADAHONDA ES')
Uber_Trip = accumulate_movements('Taxi y Carsharing')
Uber_Eats = accumulate_movements('Pago en UBER *EATS')
Bizum = accumulate_movements('Transferencia Bizum emitida')
Restaurants_Bars = accumulate_movements('Cafeterías y restaurantes') + accumulate_movements('Supermercados y alimentación') - Eating_Out_Work - Uber_Eats

# Cafeterías y restaurantes" + "Supermercados y alimentacion" - "Eating out Work")

# Print in screen
print(f'\n\n----------------------\nACCUMULATED EXPENSES\n----------------------\n')
print(f'    * Eating out (Work):  {Eating_Out_Work:.2f} €')
print(f'    * Uber Trips:  {Uber_Trip:.2f} €')
print(f'    * Bizum:  {Bizum:.2f} €')
print(f'    * Uber Eats:  {Uber_Eats:.2f} €')
print(f'    * Restaurants Bars:  {Restaurants_Bars:.2f} €')
print(f'\n------------------\n\n')