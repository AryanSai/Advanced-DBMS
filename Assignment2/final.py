import csv, re

def parse_query(query):
    parsed_query = {}
    # strip - remove leading and trailing spaces
    # group(1) - the first group of regular expression 
    
    select_arg = re.search(r'SELECT (.+?) FROM', query)
    if select_arg:
        parsed_query['SELECT'] = select_arg.group(1).strip().split(', ')
    else:
        print("SELECT clause not found")

    from_arg = re.search(r'FROM (.+?)(?: WHERE| ORDER BY| ;|$)', query)
    if from_arg:
        parsed_query['FROM'] = from_arg.group(1).strip()
    else:
        print("FROM clause not found")

    where_arg = re.search(r'WHERE (.+?)(?: ORDER BY|$)', query)
    if where_arg:
        parsed_query['WHERE'] = where_arg.group(1).strip()

    order_arg = re.search(r'ORDER BY (.+?)$', query)
    if order_arg:
        parsed_query['ORDER BY'] = order_arg.group(1).strip()

    return parsed_query

def execute_select(reader,select_clause,columns):
    if select_clause[0] == '*': # Handling SELECT * clause
            for row in reader:
                print(row)
    else: # Handling SELECT {col1, col2, ...} clause
        dict = {column: index for index, column in enumerate(columns)}
        for row in reader:
            print([row[dict[attr]] for attr in select_clause])


def execute(parsed_query):
    # extracting the names of the csv files
    from_clause=parsed_query['FROM']
    print("FROM clause:", from_clause)
    
    # opening the csv files
    with open(from_clause) as csvfile:
        reader = csv.reader(csvfile)
        columns = next(reader)
        print('The columns in the table are: ',columns)
        
        select_clause = parsed_query['SELECT']
        print("SELECT clause:", select_clause)
        
        execute_select(reader,select_clause,columns)
        
# WHERE student.class = 'I MTech' ORDER BY student.reg_no ASC
# name, class
def main():
    sql_query = "SELECT name, class FROM student.csv ;"
    parsed_query = parse_query(sql_query)
    print("Parsed Query:", parsed_query)
    
    execute(parsed_query)

main()