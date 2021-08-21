#
# Copyright 2020 Fatih Atalay
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at:
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#



import pandas as pd

sales = pd.read_csv("C:\\Users\\atala\\Downloads\\eBayOrdersReport.csv",skiprows=range(1))


#drop the first empty line
sales=sales.drop(sales.index[0])
#drop last 3 lines which are not orders
sales=sales.drop(sales.index[[-1,-2,-3]])


print(list(sales.columns) )

# 1 - Prefixing Quantity in the Custom Label Column
# Change column quantity from float>int>str.
sales['Quantity'] = sales['Quantity'].astype(int).astype(str)
# Prefixing Qty in the CustomLabel Column
for index, row in sales.iterrows():
   if (row['Quantity'] != '1' and row['Custom Label'] != ''):
       row['Custom Label'] = str(row['Quantity']) + 'x ' + str(row['Custom Label'])


# 2 - Combine Mutiple Item Purchases (within same order)
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
            else:
                cart = "* " + sales.loc[j+1, 'Custom Label'] + cart
                sales.loc[j+1, 'Custom Label'] = ""
            j += 1
            i = j
        sales.loc[k+1, 'Custom Label'] = cart
        print(cart)
    i += 1


# 3 - Combine Mutiple orders from same buyer.

# add a column to identify multiple orders from the same buyer that ships to the same address.
sales['mult_order'] = 0


i=1
for j in range(i + 1, sales.shape[0] + 1):
    if (sales.loc[i, 'Buyer Username'] == sales.loc[j, 'Buyer Username']) and \
            (sales.loc[i, 'Ship To Address 1'] == sales.loc[j, 'Ship To Address 1']):
        sales.loc[i, 'mult_order'] = i
        sales.loc[j, 'mult_order'] = i



for i in range(2, sales.shape[0]+1):
    for j in range(i+1, sales.shape[0]+1):
        if sales.loc[i, 'mult_order'] != 0:
            pass
        elif (sales.loc[i,'Buyer Username'] == sales.loc[j, 'Buyer Username'] )and \
                (sales.loc[i, 'Ship To Address 1'] == sales.loc[j, 'Ship To Address 1']):
            sales.loc[i, 'mult_order'] = i
            sales.loc[j, 'mult_order'] = i

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
        print (cart)

#drop the multiple order identifier column

sales.drop('mult_order',1, inplace=True)


sales.to_csv("C:\\Users\\atala\\Downloads\\eBayOrdersprocessed.csv", index=False)
