import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
import random
import xlsxwriter
import xlrd
import openpyxl

dfs=[]
## These will help create the urls
Play=['all','ev','pp'] # All Strength, Even Strength, Power Play
Date=range(2007,2022) # the range functions goes up to the second number - 1,
                      # so I put 2022 for the 2021 season
Count_Rate=['n','y'] # n=count, y=rates

# The actual scraping part
for date in Date:
    # Transform the dates in the season, like 20202021 for example
    season=f"{date}"+f"{date+1}"
    for play in Play:
        for countrate in Count_Rate:
            # Insert the strings into the url
            url=f"http://naturalstattrick.com/playerteams.php?fromseason={season}&thruseason={season}&stype=2&sit={play}&score=all&stdoi=std&rate={countrate}&team=ALL&pos=S&loc=B&toi=0&gpfilt=none&fd=&td=&tgp=410&lines=single&draftteam=ALL"
            time.sleep(random.uniform(15,30))
            # Read the data into a panda dataframe, and then 
            # inserting the year and other variables to identify the parameters for that df
            if play=='all':
                if countrate=='n':
                    df1 = pd.read_html(url, header=0, index_col = 0, na_values=["-"])[0]
                    df1.insert(0, 'Season', f'{season}')
                else:
                    df2 = pd.read_html(url, header=0, index_col = 0, na_values=["-"])[0]
                    df3 = pd.concat([df1,df2], axis=1)
                    df3 = df3.loc[:,~df3.columns.duplicated()]
            elif play=='ev':
                if countrate=='n':
                    df4 = pd.read_html(url, header=0, index_col = 0, na_values=["-"])[0]
                else:
                    df5 = pd.read_html(url, header=0, index_col = 0, na_values=["-"])[0]
                    df6 = pd.concat([df4,df5], axis=1)
                    df6 = df6.loc[:,~df6.columns.duplicated()]
                    df6 = df6.T.tail(57).T
            else:
                if countrate=='n':
                    df7 = pd.read_html(url, header=0, index_col = 0, na_values=["-"])[0]
                else:
                    df8 = pd.read_html(url, header=0, index_col = 0, na_values=["-"])[0]
                    df9 = pd.concat([df7,df8], axis=1)
                    df9 = df9.loc[:,~df9.columns.duplicated()]
                    df9 = df9.T.tail(57).T
                    df10 = pd.concat([df3,df6,df9], axis=1)
                    dfs.append(df10)
            # Including these print comments just do you can see your progress
            # I know it's not super correct, like "pp strength", aka, power play
            # strength is not a thing, but you know what it's supposed to mean
            print(f'done with {play} {countrate}')
    print(f'done with season {season}')

## Concatenate all of those dataframes                     
df = pd.concat(dfs)

## group the data by player, and then retrieve the groups to separate players
## into different data frames, all put into a dictionary

## Change column names for JSON access 
y=list(df.columns)
for i in range(0,len(y)):
    x=y[i]
    x=x.replace('/GP','PerGP')
    x=x.replace('%','Pct')
    x=x.replace('/60','PerSixty')
    x="".join(x.split())
    y[i]=x
df.columns=y

## 
df.Player=df.Player.apply(lambda row : row.title())
grouped=df.groupby(df.Player)
players={}
## Creating a second dictionary to later alphabetically sort the dfs
players2={}

## Get each player's data
for name in list(df.Player.unique()):
    players[name]=grouped.get_group(name)

## Both sort alphabetically in new dict, but also sort data in each by Season
for name in sorted(list(players.keys())):
    players2[name]=players[name].sort_values(by=['Season'])
    
## Drop the player column since we don't need it for sheets
for name in players2.keys():
    players2[name]=players2[name].drop(['Player'], axis=1).set_index('Season')
    
writer = pd.ExcelWriter('NHL.xlsx', engine='xlsxwriter')

for name in list(players2.keys()):
    players2[name].to_excel(writer, sheet_name=name, index=True)

writer.save()

