
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
        - Bazar

	- Subscriprion
		- Psychologist (Check wether there's a 210 withdrawal in "Cajeros")
		- Dystopia (Check wether there's a 15 movement in "Transferencia Bizum emitida")
		- ChatGPT ("Pago en CHATGPT SUBSCRIPTION")
        - Gym
        - Public transport

    - Untracked
        - "Total" - "Accumulated Spendings"

'''

import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime



############################################### Variables ###############################################

# Flags
Print_to_cmd = False
Print_Pie_Graphs = True
Print_expenses_vs_time = True
Log_On_Excel = False


########################################## Function definitions ##########################################

def accumulate_movements (Concept, df):
    
    """
    This function looks for movements with a certain type of concept (str) and returns the 
    accumulated expenses for all movements found. It doesn't require that the concept be 
    specified on a certain column

    Parameters
    ----------
    Concept : str
        Concept of the movement as stated in the df
    df : dataframe
        Dataframe where this information should be searched at
    Returns
    -------
    float
        Sum of all movements under the same Concept.
    """

    # Create a boolean series indicating matches for the subcategory we are interested in
    # Don't ask the user to specify the columns, simply search in both columns
    Indexing_Series_subcat = df['SUBCATEGORÍA'] == Concept
    Indexing_Series_decrip = df['DESCRIPCIÓN'] == Concept

    # Then use only the one that contains any instances of the concept 
    if (Indexing_Series_subcat.any()):

        # Trim out any rows that do not contain any instances
        filtered_df = df[Indexing_Series_subcat]
    
        # Return all expenses for the specified instance
        return filtered_df['IMPORTE (€)'].sum()

    elif (Indexing_Series_decrip.any()):
        filtered_df = df[Indexing_Series_decrip]
        # Return all expenses for the specified instance
        return filtered_df['IMPORTE (€)'].sum()

    else:
        return 0.0



def find_movement (Amount, Concept, df):

    """
    This function search for a movement of a specified Amount under a certain Concept.
    There is no need for the user to specify the column the Concept is located at

    Parameters
    ----------
    Amount : float
        Amount of € (signed) to look for in the df of bank movements.
    Concept : str
        Concept of the movement as stated in the df
    df : dataframe
        Dataframe where this information should be searched at

    Returns
    -------
    list floats
        List of all matching movements.
    """

    Indexing_Series_subcat = df['SUBCATEGORÍA'] == Concept
    Indexing_Series_decrip = df['DESCRIPCIÓN'] == Concept

    # Then use only the one that contains any instances of the concept 
    if (Indexing_Series_subcat.any()):
        # Trim out any rows that do not contain any instances
        filtered_df = df[Indexing_Series_subcat]

        # Filter out the df from all movements that don't match the amount
        Indexing_Series_Amount = filtered_df['IMPORTE (€)'] == Amount
        filtered_df = filtered_df[Indexing_Series_Amount]

        # Cast to list in case there are more than one movement matching
        return filtered_df['IMPORTE (€)'].tolist()

    elif (Indexing_Series_decrip.any()):
        filtered_df = df[Indexing_Series_decrip]
        # Filter out the df from all movements that don't match the amount
        Indexing_Series_Amount = filtered_df['IMPORTE (€)'] == Amount
        filtered_df = filtered_df[Indexing_Series_Amount]

        # Cast to list in case there are more than one movement matching
        return filtered_df['IMPORTE (€)'].tolist()

    else:
        return [0.0]



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


####################################################### MAIN CODE ###########################################################



################################# Dynamicaly read files on subfolder "Bank_Monthly_Movements" ###############################

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

# Check whether the output file exists
Output_path = os.path.join(current_directory, 'Output')
Tracked_expenses_path = 'Tracked_expenses.xlsx'
Tracked_expenses_path = os.path.join(Output_path, Tracked_expenses_path)

if not os.path.exists(Tracked_expenses_path):

    # If not create empty dict
    Output_dic = {
        ("Month", "/"): [],
        ("Savings", "/"): [],
        ("Eating Out Work", "/"): [],
        ("Uber To Work", "/"): [],
        ("Recreational", "Uber Eats"): [],
        ("Recreational", "Bars And Restaurants"): [],
        ("Recreational", "Bizum"): [],
        ("Recreational", "Bazar"): [],
        ("Subscriptions", "Psychologist"): [],
        ("Subscriptions", "Dystopia"): [],
        ("Subscriptions", "ChatGPT"): [],
        ("Subscriptions", "Gym"): [],
        ("Subscriptions", "Public Transport"): [],
        ("Unaccounted", "Withdrawals"): [],
        ("Unaccounted", "Unknown"): [],
        ("Income", "Salary"): [],
        ("Income", "Bizums"): [],
        ("Total Sum Acc", "/"): [],
        ("Balance", "/"): []
    }

# If it does it exist read it into a dict to append new data
else:
    Output_df = pd.read_excel(Tracked_expenses_path, header=[0, 1], index_col=0)
    Output_dic = Output_df.to_dict(orient='list')


######################################## Accumulate and find payments for each month ########################################

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
for date in Dates:
    month, year = date[0], date[1]

    # Apply the funciton to each element and pass month as an additional argument
    Indexing_df = Dates_df.apply(Index_by_month, args=(month, year))

    # Create a dataframe for each month with each indexing series
    Month_df = Movements_df[Indexing_df] 

    # Payments through Bizum and Withdrawals:
    # This payments have to be individualy serached in the list of movements
    Psychologist = sum( find_movement (Amount = -210.00, Concept = 'Cajeros', df = Month_df) )
    Dystopia = sum( find_movement (Amount = -15.00, Concept = 'Transferencia Bizum emitida', df = Month_df) )

    # Find all instances of movements for each category and add them into one single value
    Eating_Out_Work = ( accumulate_movements('Pago en CAFET. IMDEA NANOCIENCIA MADRID ES', Month_df) 
                       + accumulate_movements('Pago en LA ESTACION DE MAJADAHONDMAJADAHONDA ES', Month_df)
                       + accumulate_movements('Pago en DELIKIA VINCIOS ES', Month_df))
    
    Uber_Trip = accumulate_movements('Taxi y Carsharing', Month_df)
    
    Uber_Eats = accumulate_movements('Pago en UBER *EATS', Month_df)
    
    Bizum = accumulate_movements('Gasto Bizum', Month_df)
    
    Restaurants_Bars = (accumulate_movements('Cafeterías y restaurantes', Month_df)
                        - Eating_Out_Work - Uber_Eats)
    
    Withdrawals = (accumulate_movements('Cajeros', Month_df) - Psychologist)

    Bazar = ( accumulate_movements('Gasolina y combustible', Month_df) 
             + accumulate_movements('Supermercados y alimentación', Month_df) 
             + accumulate_movements('Regalos y juguetes', Month_df) )
    
    ChatGPT = accumulate_movements('Pago en CHATGPT SUBSCRIPTION', Month_df)
    
    Gym = ( accumulate_movements('Recibo ALTAFIT GRUPO DE GESTION S.L', Month_df) 
           + accumulate_movements('Pago en ALTAFIT MAJADAHONDA MAJADAHONDA ES', Month_df) )
    
    Public_Transport = accumulate_movements('Transporte público', Month_df)

    Salary = accumulate_movements('Nomina recibida FUNDACION IMDEA NANOCIENCIA', Month_df)

    Bizum_received = accumulate_movements('Ingreso Bizum', Month_df)

    # Tally up
    Expenses_Accounted = ( Eating_Out_Work + Uber_Trip + Uber_Eats + Bizum + Restaurants_Bars + Bazar 
                       + ChatGPT + Gym + Psychologist  + Public_Transport + Dystopia + Withdrawals )

    Balance = Month_df['SALDO (€)'].tolist()[0] - Month_df['SALDO (€)'].tolist()[-1]
    Expenses_Total = Balance - Salary - Bizum_received
    Expenses_Unaccounted = Expenses_Total - Expenses_Accounted



    ################################################## Sort and store results #############################################

    # Append data to dict
    Output_dic[("Month", "/")].append(datetime(year, month, 1))
    Output_dic[("Savings", "/")].append(0.0)
    Output_dic[("Eating Out Work", "/")].append(Eating_Out_Work)
    Output_dic[("Uber To Work", "/")].append(Uber_Trip)
    Output_dic[("Recreational", "Uber Eats")].append(Uber_Eats)
    Output_dic[("Recreational", "Bars And Restaurants")].append(Restaurants_Bars)
    Output_dic[("Recreational", "Bizum")].append(Bizum)
    Output_dic[("Recreational", "Bazar")].append(Bazar)
    Output_dic[("Subscriptions", "Psychologist")].append(Psychologist)
    Output_dic[("Subscriptions", "Dystopia")].append(Dystopia)
    Output_dic[("Subscriptions", "ChatGPT")].append(ChatGPT)
    Output_dic[("Subscriptions", "Gym")].append(Gym)
    Output_dic[("Subscriptions", "Public Transport")].append(Public_Transport)
    Output_dic[("Unaccounted", "Withdrawals")].append(Withdrawals)
    Output_dic[("Unaccounted", "Unknown")].append(Expenses_Unaccounted)
    Output_dic[("Income", "Salary")].append(Salary)
    Output_dic[("Income", "Bizums")].append(Bizum_received)
    Output_dic[("Total Sum Acc", "/")].append(Expenses_Accounted)
    Output_dic[("Balance", "/")].append(Balance)

    Output_df = pd.DataFrame.from_dict(Output_dic)


    
    ############################################# Visualize results #############################################

    # Print into cmd
    if (Print_to_cmd):
        print(f'\n\n*************************************\n        ACCUMULATED EXPENSES\n')
        print(f'              {month}/{year}\n*************************************\n')
        print(f'    * Savings:  {0:.2f} €')
        print(f'    * Eating out (Work):  {Eating_Out_Work:.2f} €')
        print(f'    * Uber Trips:  {Uber_Trip:.2f} €')
        print(f'    * Uber Eats:  {Uber_Eats:.2f} €')
        print(f'    * Bars and Restaurants:  {Restaurants_Bars:.2f} €')
        print(f'    * Bizum:  {Bizum:.2f} €')
        print(f'    * Bazar:  {Bazar:.2f} €')
        print(f'    * Psychologist:  {Psychologist:.2f} €')
        print(f'    * Dystopia:  {Dystopia:.2f} €')
        print(f'    * ChatGPT:  {ChatGPT:.2f} €')
        print(f'    * Gym:  {Gym:.2f} €')
        print(f'    * Public Transport:  {Public_Transport:.2f} €')
        print(f'    * Withdrawals:  {Withdrawals:.2f} €')
        print(f'\n--------------------------------------\n')
        print(f'    * Total sum:  {Expenses_Total:.2f} €')
        print(f'    * Balance:  {Balance:.2f} €')
        print(f'\n--------------------------------------\n')
        print(f'    * Unaccounted movements:  {Expenses_Unaccounted:.2f} €')
        print(f'\n*************************************\n\n')

    # Graph results

    # Pie Chart
    # Get labels for each pie slize from the df headers
    labels = Output_df.columns.tolist()

    # This chart shouldn't show computed values like dates, Incomes, Computations, etc... 
    labels = labels[1:-4]

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

    # Get sizes for pie slizes from the row content of the df
    sizes = Output_df.iloc[-1].tolist()

    # This chart shouldn't show computed values like dates, incomes, Balance, Total sum, etc... 
    sizes = sizes[1:-4]

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

    # 'labels' is a list storing tuples, It's first element contains a columns category. To count how many subcategories 
    # are per category we iterate over the list and count how many times every category is repeated, check "Tracking_dic" structure
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

    # Since logging counts is done upon comparison at the second step we need one last log at the end
    # (I need to test if this hack works for all cases)
    subcat_count = np.append(subcat_count, count)
    

    # A handpicked list of 'sequential' colormaps that don't clash with pie slice neighbours
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
        color = cmap( np.linspace(0.3, 0.6, int(subcat_count[i])) )

        # Deal with starting case when there's nothing to stack
        if (i==0):        
            # Store first colormap
            colors = color

        # Continue as normal for the rest of indexes
        else:    
            # Concatenate both arrays
            colors = np.vstack((colors, color))

    # Create a pie chart
    if (Print_Pie_Graphs):

        fig, ax = plt.subplots()

        # Explode wedges that are small enough, so that their labes don't clash with each other
        explode_wedges = []
        for size in sizes:
            if (size != 0):
                explode_wedges.append( 10 / size )
            
            else:
                explode_wedges.append(0)

        ax.pie(sizes, labels=labels_curated, colors=colors, autopct='%1.1f%%', shadow=False, pctdistance=0.6, labeldistance=1.1, explode=explode_wedges)
        
        # Add a circle in the center to make a 'donut' instead of a 'pie'
        my_circle=plt.Circle( (0,0), 0.75, color='white')
        p=plt.gcf()
        p.gca().add_artist(my_circle)

        ax.set_title(label = f'Expenses distribution\nMonth : {month}/{year}')



# Write compiled data into the Output excel sheet
if (Log_On_Excel):
    Output_df.to_excel(Tracked_expenses_path)


# Create a graph showing evolution of explenses over time
if (Print_expenses_vs_time):
    
    fig, ax = plt.subplots()

    # Extract expenses from dict into list to iterate later while referencing them
    # Convert dictionary items to a list
    items_list = list(Output_dic.items())
    Expenses = []

    # Sum all expenses iteratively to construct fill curves
    dates = Output_dic[("Month", "/")]
    acc_expense = np.zeros( shape = len( dates ) )
    # Skip dates, incomes, sum and balance
    for _, expense in items_list[1:-4]:

        # Cast to array to sum element wise
        curr_expense = np.array(expense)
        acc_expense = curr_expense + acc_expense
        Expenses.append(acc_expense)

    # Compare expanses to income
    Income = np.array(Output_dic[("Income", "Salary")]) + np.array(Output_dic[("Income", "Bizums")])
    plt.plot(dates, Income, color='k', label="Income")
    # Emphasize zero crossing
    plt.plot(dates, np.zeros(shape=len(dates)), color='red', alpha=0.5)

    # Start to fill from the income line downwards to signify the progressive drain of income
    Balances = [Income]
    for expense in Expenses:
        Balances.append(Income + expense)

    # Fill between each line
    for i in range(0, len(Balances)-1):

        # Dates are shared as a horizontal axis for all curves
        plt.fill_between( dates , Balances[i], Balances[i+1], color=colors[i], label=labels_curated[i])

    plt.xticks(dates)
    plt.xlabel('Months')
    plt.ylabel('Balance [€]')
    plt.legend()

# Display the plot
plt.show()
