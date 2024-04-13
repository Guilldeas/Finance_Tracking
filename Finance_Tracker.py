
'''
Track spendings

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
    
    """
    This function looks for movements with a certain type of concept (str) and returns the 
    accumulated expenses for all movements found. It doesn't require that the concept be 
    specified on a certain column

    Parameters
    ----------
    Concept : str
        Concept of the movement as stated in the df

    Returns
    -------
    float
        Sum of all movements under the same Concept.
    """

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



def find_movement (Amount, Concept):

    """
    This function search for a movement of a specified Amount under a certain Concept.
    There is no need for the user to specify the column the Concept is located at

    Parameters
    ----------
    Amount : float
        Amount of € (signed) to look for in the df of bank movements.
    Concept : str
        Concept of the movement as stated in the df

    Returns
    -------
    list floats
        List of all matching movements.
    """

    Indexing_Series_subcat = Movements_df['SUBCATEGORÍA'] == Concept
    Indexing_Series_decrip = Movements_df['DESCRIPCIÓN'] == Concept

    # Then use only the one that contains any instances of the concept 
    if (Indexing_Series_subcat.any()):
        # Trim out any rows that do not contain any instances
        filtered_df = Movements_df[Indexing_Series_subcat]

    elif (Indexing_Series_decrip.any()):
        filtered_df = Movements_df[Indexing_Series_decrip]
    
    # Filter out the df from all movements that don't match the amount
    Indexing_Series_Amount = filtered_df['IMPORTE (€)'] == Amount
    filtered_df = filtered_df[Indexing_Series_Amount]

    # Cast to list in case there are more than one movement matching
    return filtered_df['IMPORTE (€)'].tolist()
    




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
Movements_df['IMPORTE (€)'] = Movements_df['IMPORTE (€)'].astype(float)
Movements_df['SALDO (€)'] = Movements_df['SALDO (€)'].astype(float)

# Find all instances of movements due to Uber rides
Eating_Out_Work = accumulate_movements('Pago en CAFET. IMDEA NANOCIENCIA MADRID ES') + accumulate_movements('Pago en LA ESTACION DE MAJADAHONDMAJADAHONDA ES')
Uber_Trip = accumulate_movements('Taxi y Carsharing')
Uber_Eats = accumulate_movements('Pago en UBER *EATS')
Bizum = accumulate_movements('Transferencia Bizum emitida')
Restaurants_Bars = accumulate_movements('Cafeterías y restaurantes') + accumulate_movements('Supermercados y alimentación') - Eating_Out_Work - Uber_Eats
ChatGPT = accumulate_movements('Pago en CHATGPT SUBSCRIPTION')

# Payments through Bizum and Withdrawals:
# This payments have to be individualy serached in the list of movements
Psychologist = sum( find_movement (Amount = -210.00, Concept = 'Cajeros') )
Dystopia = sum( find_movement (Amount = -15.00, Concept = 'Transferencia Bizum emitida') )

# Tally up
Total_accounted = Eating_Out_Work + Uber_Trip + Uber_Eats + Bizum + Restaurants_Bars + ChatGPT + Psychologist + Dystopia

# Total sum of movements is the balance at the begining of the list minus at the end of the list
Balance = Movements_df['SALDO (€)'].tolist()[0] - Movements_df['SALDO (€)'].tolist()[-1]
Unaccounted = Balance - Total_accounted


# Print in screen
print(f'\n\n*************************************\n        ACCUMULATED EXPENSES\n*************************************\n')
print(f'    * Eating out (Work):  {Eating_Out_Work:.2f} €')
print(f'    * Uber Trips:  {Uber_Trip:.2f} €')
print(f'    * Bizum:  {Bizum:.2f} €')
print(f'    * Uber Eats:  {Uber_Eats:.2f} €')
print(f'    * Restaurants Bars:  {Restaurants_Bars:.2f} €')
print(f'    * Psychologist:  {Psychologist:.2f} €')
print(f'    * Dystopia:  {Dystopia:.2f} €')
print(f'    * ChatGPT:  {ChatGPT:.2f} €')
print(f'\n--------------------------------------\n')
print(f'    * Total sum:  {Total_accounted:.2f} €')
print(f'    * Balance:  {Balance:.2f} €')
print(f'\n--------------------------------------\n')
print(f'    * Unaccounted movements:  {Unaccounted:.2f} €')
print(f'\n*************************************\n\n')
