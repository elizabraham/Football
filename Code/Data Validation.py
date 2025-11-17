import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


#Getting raw data from source path
df = pd.read_excel(r"C:\Users\elizabeth\Documents\personal\HOME\tasks\SA - Data for Task 1.xlsx")
print(df.columns)

#Column Analysis

#Counting number of rows and columns
#r =100  c= 52
r,c = df.shape
#print(r,c)

#Checking level of data
#100 : matches no of rows in table
#LOD: VIN, TRANSACTION_ID
unique_count = df[["VIN","TRANSACTION_ID"]].drop_duplicates().shape[0]
#print(unique_count)

#Describing the data
#print(type(df.columns))
#print(df.describe())

#Datatypes of the data
#print(df.dtypes)

#No of unique values
for col in df.columns:
    print(col,":",df[col].nunique())


