import numpy as np
import matplotlib.pyplot as plt

list = ["a", "b", "b", "b", "b"]

list = ["b", "b", "a", "b", "a", "b", "b"]

# Sample data
labels = ['Category A_1', 'Category A_2', 'Category B', 'Category C', 'Category D', 'Category E_1', 'Category E_2']
sizes = [215, 130, 245, 210, 300, 230, 245]  # Example data points for the pie chart


# Construct color maps for each 'Category' of tracked data
# The "colormap" argument in pie() takes an array of numerical values indicating color.
# We want to use a specific gradient for each category, the cmap() will output   
subcat_count = np.empty(0)
count = 0
previous_char = "start"

for index in range(0, len(list)):

    # Whenever we come into an "a" from another "a" or if we start from an "a" we log "1"
    if (list[index] == "a" and previous_char == "a") or ( list[index] == "a" and previous_char == "start" ):
        subcat_count = np.append(subcat_count, 1)
        previous_char = list[index]
    
    # Whenever we come into a "b" from an "a" or if we start from a "b" we start counting how many consecutive "b"
    if (list[index] == "b" and previous_char == "a") or ( list[index] == "b" and previous_char == "start" ) or (list[index] == "b" and previous_char == "b"):
        count = count + 1
        previous_char = list[index]

    # Whenever we come into an "a" from a "b" we stop counting, log how many consecutive "b" and log the "a"
    if (list[index] == "a" and previous_char == "b"):
        subcat_count = np.append(subcat_count, count)
        subcat_count = np.append(subcat_count, 1)
        count = 0
        previous_char = list[index]

    # Deal with end cases
    if (index == len(list) - 1):

        if(list[index] == "a"):
            subcat_count = np.append(subcat_count, 1)
        
        else:
            subcat_count = np.append(subcat_count, count)

cmap_1 = plt.get_cmap('Oranges')
cmap_2 = plt.get_cmap('Blues')
cmap_3 = plt.get_cmap('Greys')
cmap_5 = plt.get_cmap('Reds')
cmap_4 = plt.get_cmap('Greens')

cmaps = [cmap_1, cmap_2, cmap_3, cmap_4, cmap_5]

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
ax.pie(sizes, labels=labels, colors=colors)

# Display the plot
plt.show()

