
#####################################################################################################################################################   
# Stocks and Databases and Data Visualization
#
# Data is read from a file to database 
# Data is read from the database into data structures
# Data from data structures is output to file in tables
# Data from json file is read and added to database file and output in a matplotlib graph
# Data from json file calculations are output to a Plotly interactive graph
#####################################################################################################################################################

# imports
from cProfile import label
from inspect import trace
from wsgiref import headers
from tabulate import tabulate
from datetime import date, datetime
import csv
import sqlite3
import pandas as pd
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator)
import plotly.graph_objects as G

#######################################################################################################################################

# file names
stocks_file = 'Lesson6_Data_Stocks.csv'
bonds_file = 'Lesson6_Data_bonds.csv'
db_file = 'Week10.db'
graph_file = 'Week10_Output.png'
json_file = 'AllStocks.json'
table_file = 'Table_Output.txt'

# Stocks class
class Stocks:
    def __init__(self, purchaseID, stock, shares, purchPrice, curPrice, purchDate):
        self.purchaseID = purchaseID
        self.stock = stock
        self.shares = shares
        self.purchPrice = purchPrice
        self.curPrice = curPrice
        self.purchDate = purchDate
	
	# gains losses function
    def gains_losses(self):
        return (('{:.2f}').format((self.curPrice - self.purchPrice) * self.shares))
	
    # yearly earnings function
    def yearly_earn_loss(self):
        today = datetime.strftime(date.today(), '%m/%d/%Y')
        day_diff = (datetime.strptime(today, '%m/%d/%Y') - datetime.strptime(self.purchDate, '%m/%d/%Y')).days
        return ('{:.2f}').format(((((self.curPrice - self.purchPrice) / self.purchPrice) / (day_diff/365))) * 100)
	
# Bonds class
class Bonds(Stocks):
    def __init__(self, purchaseID, stock, shares, purchPrice, curPrice, purchDate, coupon, peryield):
        super().__init__(purchaseID, stock, shares, purchPrice, curPrice, purchDate)
        self.coupon = coupon
        self.peryield = peryield
		
# Investor class		
class Investor:
    def __init__(self, investorID, name, address, phone):
        self.investorID = investorID
        self.name = name
        self.address = address
        self.phone = phone
        self.stockList = []
        self.bondList = []
		
    def addStock(self, newStock):
        self.stockList.append(newStock)
	
    def addBond(self, newBond):
        self.bondList.append(newBond)

#####################################################################################################################################
# create first investor 
#####################################################################################################################################
p1 = Investor(1,'Bob Smith','123 address','9999999999')

stock_db = []
bond_db = []

#####################################################################################################################################
# open files and read data 
#####################################################################################################################################

def read_stocks():
    try:
        with open(stocks_file, 'r',) as infile:
            # add stocks from file
            reader = csv.reader(infile, delimiter = ',') 
            next(infile)
            #purchase id for stocks
            s = 1

            for row in reader:
                stock_db.append([p1.investorID, s, row[0], row[1], row[2], row[3], row[4]])
                s += 1

    except IOError:
        print('\nStocks Input File Not Found!!!\n')
        exit()


def read_bonds():
    try:
        with open(bonds_file, 'r',) as infile2:
            # add stocks from file
            reader2 = csv.reader(infile2, delimiter = ',') 
            next(infile2)
            #purchase id for bonds
            b = 1

            for row2 in reader2:
                bond_db.append([p1.investorID, b, row2[0], row2[1], row2[2], row2[3], row2[4], row2[5], row2[6]])
                b += 1
            
    except IOError:
        print('\nBonds Input File Not Found!!!\n')
        exit()

read_stocks()
read_bonds()
#####################################################################################################################################################
# Connect to database, create tables, insert values from file into table
#####################################################################################################################################################

# connect to database
try:
    connection = sqlite3.connect(db_file)
    
except sqlite3.Error as error:
    print("Error while connecting to sqlite", error)
    exit()

cursor = connection.cursor()

# create tables
try:
    cursor.execute('DROP TABLE IF EXISTS Investors')
    cursor.execute('DROP TABLE IF EXISTS Stocks')
    cursor.execute('DROP TABLE IF EXISTS Bonds')
    cursor.execute('DROP TABLE IF EXISTS Stocks_JSON')

    cursor.execute('''CREATE TABLE Investors (
                            name text,
                            phone_number text,
                            address text,
                            investor_id integer);''')

    cursor.execute('''CREATE TABLE Stocks (
                            investor_id integer,
                            stock_id,
                            symbol text,
                            no_shares integer,
                            purchase_price float,
                            current_price float,
                            purchase_date text);''')

    cursor.execute('''CREATE TABLE Bonds (
                            investor_id integer,
                            bond_id,
                            symbol text,
                            no_shares float,
                            purchase_price float,
                            current_price float,
                            purchase_date float,
                            coupon float,
                            per_yield float);''')

    # create table for AllStocks.json file
    cursor.execute('''CREATE TABLE Stocks_JSON (
                            symbol text,
                            date text,
                            open float,
                            high float,
                            low float,
                            close float,
                            volume float);''')
except Exception as error:
    print('Table Creation Error.')
    exit()

# insert data from file to tables
try:              
    inv_tuple = (p1.name, p1.phone, p1.address, p1.investorID)
    cursor.execute('INSERT INTO Investors VALUES (?, ?, ?, ?)', inv_tuple)
    print('Investor inserted')

    for stck in stock_db:
        stock_tuple = (stck[0], stck[1] , stck[2], stck[3], stck[4], stck[5], stck[6])
        cursor.execute('INSERT INTO Stocks VALUES (?, ?, ?, ?, ?, ?, ?)', stock_tuple)
    print('Stock inserted')

    for bnd in bond_db:
        bond_tuple = (bnd[0], bnd[1] , bnd[2], bnd[3], bnd[4], bnd[5], bnd[6], bnd[7], bnd[8])
        cursor.execute('INSERT INTO Bonds VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', bond_tuple)
        print('Bond inserted')

    connection.commit()

except Exception as error:
    print('Insert Error')
    exit()

connection.close()

#####################################################################################################################################################
# Read table data into data structures
#####################################################################################################################################################

# connect to database
try:
    connection = sqlite3.connect(db_file)
    
except sqlite3.Error as error:
    print('Error while connecting to sqlite', error)
    exit()

cursor = connection.cursor()

try:

    # get stocks from table
    cursor.execute(("SELECT * FROM Stocks"))
    stock_rows = cursor.fetchall()

    try:
        for stock in stock_rows:
            p1.addStock(Stocks(stock[1], stock[2], int(stock[3]), float(stock[4]), float(stock[5]), stock[6])) 
    except ValueError:
            print('\nValueError: Check stock input value types')
            print('-> Shares need to be integer type\n-> Purchase price and Current value need to be float type\n')
            exit()

    #get bonds from table
    cursor.execute(("SELECT * FROM Bonds"))
    bond_rows = cursor.fetchall()
    try:
        for bond in bond_rows:
            p1.addBond(Bonds(bond[1], bond[2], int(bond[3]), float(bond[4]), float(bond[5]), bond[6], float(bond[7]), float(bond[8])))
    except ValueError:
        print('\nValueError: Check bond input value types')
        print('-> Shares need to be integer type')
        print('-> Purchase price, Current value, Coupon, and Yield need to be float type\n')
        exit()

except Exception as error:
    print('Table Read Error.')
    exit()

connection.close()

# append stocks and bonds to list
stockList = [['Stock', 'Share #', 'Earnings/Loss', 'Yearly Earning/Loss %']]
try:
    for stock in p1.stockList:
        stockList.append([stock.stock, stock.shares, stock.gains_losses(), stock.yearly_earn_loss()])
except ValueError:
    print('\nValue Error: Check input values for gains_losses and yearly_earn_loss')
    print('-> Purchase date must be mm/dd/yyyy format\n')
    exit()

# all bonds
bondList = [['Symbol', 'Quantity', 'Purchase Price', 'Current Price', 'Purchase Date', 'Coupon', 'Yield']]
for bond in p1.bondList:
    bondList.append([bond.stock, bond.shares, bond.purchPrice, bond.curPrice,
                        bond.purchDate, bond.coupon, bond.peryield])


#####################################################################################################################################################
# Output to file
#####################################################################################################################################################

try:
    # write stock and bond tables to output file
    with open(table_file, 'w',) as outfile:    
        outfile.write('\t\t\t\tStock Ownership\n')
        outfile.write(tabulate(stockList, headers='firstrow', tablefmt='github'))

        outfile.write('\n\n\n\t\t\t\t\t\t\t\t\tBond ownership for Bob Smith\n')
        outfile.write(tabulate(bondList, headers='firstrow', tablefmt='github'))

except IOError:
    print('\nOutput File Not Found!!!\n')
    exit()

#####################################################################################################################################################
# Read data from json file, output to chart
#####################################################################################################################################################

# open and read json file
with open(json_file, 'r') as allStocks_file:
    data = json.load(allStocks_file)

# add json data to database
try:
    connection = sqlite3.connect(db_file) 

except sqlite3.Error as error:
    print('Error while connecting to sqlite', error)
    exit()

cursor = connection.cursor()

# insert into table
try:
    for item in data:
        json_data = (item['Symbol'], item['Date'] , item['Open'], item['High'], item['Low'], item['Close'], item['Volume'])
        cursor.execute('INSERT INTO Stocks_JSON VALUES (?, ?, ?, ?, ?, ?, ?)', json_data)
    connection.commit()
    print('JSON inserted into table')

except Exception as error:
    print('Stocks_JSON Insert Error')
    exit()

connection.close()

# get data needed for graph 

# get all dates into list, remove duplicates, sort dates
allDates = [x['Date']for x in data]
dateList = [*set(allDates)]
dateList.sort(key=lambda date: datetime.strptime(date, '%d-%b-%y'))

# stock list and dictionary
stkList=[]
stkDict = {}
max = 0

# fill stock dictionary with stock data 
for stk in data:
    for st in p1.stockList:
        if stk['Symbol'] == st.stock:
            # price = shares * close price
            stk['Close'] = st.shares * stk['Close']

for stk in data:  
    if stk['Symbol'] not in stkList:      
        stkList.append(stk['Symbol'])
        stkDict[stk['Symbol']] = [stk['Close']]
    else:       
        stkDict[stk['Symbol']].append(stk['Close'])

    if max < len(stkDict[stk['Symbol']]):
        max = len(stkDict[stk['Symbol']])

# add none to make lengths equal
for i in stkDict.values():
    while len(i)<max:
        i.insert(0, None)

# set up graph
fig, ax = plt.subplots(figsize=(12, 8))

# plot
for i in stkDict:
    ax.plot(dateList, stkDict[i], label = i)

# set tick interval
ax.xaxis.set_major_locator(mdates.DayLocator(interval=(int(len(dateList)/9))))
ax.legend()
plt.savefig(graph_file) 


#########################################################################################################################################
# Plotly Graph
#########################################################################################################################################

# Create Plotly graph
fig = G.Figure()

def add_titles():
    fig.update_layout(title_text='Stock Values Over Time')
    fig.update_xaxes(title_text='Date')
    fig.update_yaxes(title_text='Value in USD')

def plot_data():
    for i in stkDict:
        fig.add_trace(
            G.Scatter(
                x = dateList,
                y = stkDict[i],
                name = i ,        
            )
        )

# show graph
add_titles()
plot_data()
fig.show()
    
		