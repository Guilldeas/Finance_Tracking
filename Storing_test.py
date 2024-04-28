import pandas as pd
import os



# Check whether the output file exists
current_directory = os.getcwd()
Output_path = os.path.join(current_directory, 'Output')
Tracked_expenses_path = 'Tracked_expenses.xlsx'
Tracked_expenses_path = os.path.join(Output_path, Tracked_expenses_path)

# If not create empty dic from scratch
if not os.path.exists(Tracked_expenses_path):

    Output_dic = {
        ('Recreational Expenses', 'Eating Out'): [],
        ('Recreational Expenses', 'Going to the Movies'): []
    }

# If it does exist simply read it to use it later
else:
    Output_df = pd.read_excel(Tracked_expenses_path, header=[0, 1], index_col=0)
    Output_dic = Output_df.to_dict(orient='list')


for i in range (0, 3):

    # Append each element to the list
    Output_dic[('Recreational Expenses', 'Eating Out')].append(i)
    Output_dic[('Recreational Expenses', 'Going to the Movies')].append(i)


# Store data
Output_df = pd.DataFrame.from_dict(Output_dic)
Output_df.to_excel(Tracked_expenses_path)


print(type(Output_df.columns.tolist()[0][0]))


