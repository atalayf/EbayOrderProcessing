import pandas as pd
import glob
import os
from datetime import date

# Get the latest downloaded ebay sales report 

list_of_files = glob.glob('C:\\Users\\atala\\Downloads\\eBay-OrdersReport*.csv')
latest_ebay_oders = max(list_of_files, key=os.path.getctime)

# Read the ebay sales report
sales = pd.read_csv(latest_ebay_oders, skiprows=range(1))

# Drop the first blank line
sales=sales.drop(sales.index[0])
# Drop last 3 lines which are not orders
sales=sales.drop(sales.index[[-1,-2,-3]])

# 1 - Prefixing Quantity in the Custom Label Column
# Remove the decimal point from the quantity
sales['Quantity'] = sales['Quantity'].astype(int).astype(str)

for i in range(1, sales.shape[0] + 1):
    if  pd.isnull(sales.loc[i, 'Custom Label']):
        continue
    elif sales.loc[i,'Quantity'] != '1':
        sales.loc[i,'Custom Label'] = str(sales.loc[i,'Quantity']) + 'x ' + str(sales.loc[i,'Custom Label'])

# 2 - Combine Mutiple Item Purchases (within same order) These orders have the same 'Sales Recod Number' and they
# in the consecutive lines
i=0
while i < sales.shape[0]-1:
    if (sales.iloc[i,0]) == (sales.iloc[i+1,0]):  #find multiple item orders
        k = i
        rec = sales.iloc[i,0]
        cart = ""
        j = i
        while (rec == sales.iloc[j, 0]):  # concat custom labels.
            if pd.isnull(sales.loc[j+1, 'Custom Label']):
                pass
            elif cart.startswith("*"):
                cart = cart + " + " + sales.loc[j + 1, 'Custom Label']
                sales.loc[j + 1, 'Custom Label'] = ""
            else:
                cart = "* " + sales.loc[j+1, 'Custom Label'] + cart
                sales.loc[j+1, 'Custom Label'] = ""
            j += 1
            i = j
        sales.loc[k+1, 'Custom Label'] = cart

    i += 1

# 3 - Combine Mutiple orders from same buyer.
# add a column to identify multiple orders from the same buyer that ships to the same address.

sales['mult_order'] = 0

for i in range(1, sales.shape[0]+1):
    for j in range(i+1, sales.shape[0]+1):
        if sales.loc[i, 'mult_order'] != 0:
            pass
        elif (sales.loc[i,'Buyer Username'] == sales.loc[j, 'Buyer Username']) \
                and (sales.loc[i, 'Ship To Address 1'] == sales.loc[j, 'Ship To Address 1']):
            sales.loc[i, 'mult_order'] = i
            sales.loc[j, 'mult_order'] = i

# 4 - Combine Mutiple orders from same buyer.
for i in range(1, sales.shape[0]+1):
    if sales.loc[i, 'mult_order'] >= i:
        cart=""
        for j in range(i, sales.shape[0] + 1):
            if sales.loc[j, 'mult_order'] == sales.loc[i, 'mult_order']:
                if sales.loc[j, 'Custom Label'].startswith("*"):
                    cart = "+ " + sales.loc[j, 'Custom Label'] + cart
                else:
                    cart = "* " + sales.loc[j, 'Custom Label'] + cart
                sales.loc[j, 'Custom Label']=""
        sales.loc[i, 'Custom Label'] = cart

# Drop the multiple order identifier column
sales.drop('mult_order',1, inplace=True)

today = date.today()

# Save the sales report to a csv file
sales.to_csv(f"C:\\Users\\atala\\Downloads\\eBayOrdersprocessed-{today}.csv", index=False)