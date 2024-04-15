
'''
This software tracks spendings from an ING account by reading the movements from an .xls

The spendings are grouped into the following categories:

	- Savings (0 for the moment)

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
import matplotlib.pyplot as plt
import numpy as np

########################################## Function definitions ##########################################

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



########################################## Accumulate and find payments ##########################################

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


################################################## Sort and store results #############################################

# Construct a new dataframe to track the spendings into it's categories and sub-categories
# Define the hierarchical headers with a list of tuples (Category, Subcategory). Tuples with
# no sub-categories have a placeholder "/".
Header_tuples = [
    ("Savings", "/"),
    ("Eating Out Work", "/"),
    ("Uber To Work", "/"),
    ("Recreational", "Uber Eats"),
    ("Recreational", "Bars And Restaurants"),
    ("Recreational", "Bizum"),
    ("Subscriptions", "Psychologist"),
    ("Subscriptions", "Dystopia"),
    ("Subscriptions", "ChatGPT"),
    ("Unaccounted", "/"),
    ("Total Sum", "/"),
    ("Balance", "/")
]
index = pd.MultiIndex.from_tuples(Header_tuples, names=["Category", "Subcategory"])

# Construct dataframe with sorted data
Tracking_dic = {
    ("Savings", "/"): [0],
    ("Eating Out Work", "/"): [Eating_Out_Work],
    ("Uber To Work", "/"): [Uber_Trip],
    ("Recreational", "Bars And Restaurants"): [Restaurants_Bars],
    ("Recreational", "Bizum"): [Bizum],
    ("Recreational", "Uber Eats"): [Uber_Eats],
    ("Subscriptions", "Psychologist"): [Psychologist],
    ("Subscriptions", "Dystopia"): [Dystopia],
    ("Subscriptions", "ChatGPT"): [ChatGPT],
    ("Unaccounted", "/"): [Unaccounted],
    ("Total Sum", "/"): [Total_accounted],
    ("Balance", "/"): [Balance]
}
Tracking_df = pd.DataFrame(Tracking_dic, columns=index)
print(Tracking_df)

############################################# Visualize results #############################################

# Print in screen
verbose = False
if (verbose):
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

# Graph results

# Pie Chart
# This chart shouldn't show computed values like Balance, Total sum, etc... 
Pie_df = Tracking_df.iloc[:, :-2]

# Get labels for each pie slize from the df headers
labels = Pie_df.columns.tolist()

# Labels come from a multindex tuple and therefore look like this ("Category", "Subcategory"), 
# for aesthetic purposes only subcategories are shown, if there are no subcategories the category is shown
labels_curated = []
colors = np.empty(0)
subcategory_colormap_size = 1

for header in labels:

    if (header[1] == "/"):
        labels_curated.append(header[0])
    
    else:
        labels_curated.append(header[1])

print(f"\labels = {type(labels[0])}\n")

# Get sizes for pie slizes from the row content of the df
sizes = Pie_df.iloc[0].tolist()

# Pie chart can't take negative values
for i in range(0, len(sizes)):
    sizes[i] = abs(sizes[i])

########################################## Construct colormap by categories ##########################################

# Construct color maps for each 'Category' of tracked data
# The "colormap" argument in pie() takes an ndarray indicating color.
# We want to use a specific gradient for each category, thus we compile a list counting how many subcategories per
# category
subcat_count = np.empty(0)
count = 1
previous_cat = "start"

# 'labels' is a list storing tuples, each contains the columns category followed by the sub-categories. To count how many
# subcategories are per category we take into account that categories with no subcategory store a "/" in their subcat tuple element
for index in range(0, len(labels)):
    
    # Reads the category header at the current index
    current_cat = labels[index][0]

    # At the start we can't compare categories and thus simply start the counter
    if (previous_cat == "start"):
        count = 1
        previous_cat = current_cat

    # If we find a successive category we add it to the count
    elif (current_cat == previous_cat):
        count += 1
        previous_cat = current_cat

    # If we find a different category we log the amount of subcategories
    elif (current_cat != previous_cat):
        subcat_count = np.append(subcat_count, count)
        previous_cat = current_cat
        count = 1

    # At the end we don't have a further step to compare and log so we simply log
    elif (index == len(labels)):
        subcat_count = np.append(subcat_count, count)


print(f'\nsubcat count = {subcat_count}\n')

cmap_1 = plt.get_cmap('Oranges')
cmap_2 = plt.get_cmap('Blues')
cmap_3 = plt.get_cmap('Reds')
cmap_4 = plt.get_cmap('Greens')
cmap_5 = plt.get_cmap('Purples')
cmap_6 = plt.get_cmap('Greys')


cmaps = [cmap_1, cmap_2, cmap_3, cmap_4, cmap_5, cmap_6]

# For each category create a set of colors in the same gradients
# Create as many colors are there are subcategories
colors = np.empty([1, 4])
for i in range(0, len(subcat_count)):

    # Get cmap object from list of cmaps and create an ndarray storing
    # colors for each "slice" representing the subcategories in the category
    cmap = cmaps[i]
    color = cmap( np.linspace(0.4, 0.5, int(subcat_count[i])) )

    # Deal with starting case when there's nothing to stack
    if (i==0):        
        # Store first colormap
        colors = color

    # Continue 
    else:    
        # Concatenate both arrays
        colors = np.vstack((colors, color))

print(colors)

# Create pie chart

# Create a pie chart
fig, ax = plt.subplots()
ax.pie(sizes, labels=labels_curated, colors=colors)

# Display the plot
plt.show()
