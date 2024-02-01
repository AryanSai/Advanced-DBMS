import csv

def main():
    query = 'select name,age from friends.csv;'
    tokens = query.split(' ')
    print('The given query is: ', query)
    
    select_what = tokens[tokens.index('select') + 1]  
    print(select_what)
    

main()