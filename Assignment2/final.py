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

def parse_where_condition(where_clause):
    pattern = r'(\w+)\s*(=|<|>|<=|>=)\s*(\'?)(\w+)(\'?)'
    match = re.search(pattern, where_clause)
    if match:
        column_name = match.group(1)
        comparison_operator = match.group(2)
        comparison_value = match.group(4)
        return column_name, comparison_operator, comparison_value
    else:
        return None, None, None
 
def do_operation(operator, row_value, value):
    if isinstance(row_value, int) or row_value.isdigit():
        row_value = int(row_value)
    if operator == '=':
        return row_value == int(value)
    elif operator == '>':
        return row_value > int(value)
    elif operator == '<':
        return row_value < int(value)
    elif operator == '>=':
        return row_value >= int(value)
    elif operator == '<=':
        return row_value <= int(value)

def execute_select(reader, parsed_query, columns):
    select_clause = parsed_query['SELECT']
    print("SELECT clause:", select_clause)
    
    where_clause = parsed_query.get('WHERE')  # get WHERE clause from parsed query
    print("WHERE clause:", where_clause)
    
    if where_clause:
        column, operator, value = parse_where_condition(where_clause)
        print(column, value)
        
        # get the index of the column specified in the WHERE clause
        column_index = columns.index(column)
    
    with open('output.csv', 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        if select_clause[0] == '*' or select_clause[0] == 'ALL':  # handling SELECT * clause
            csvwriter.writerow(columns)
            csvwriter.writerows(reader)
        else:  # handling SELECT {col1, col2, ...} clause
            csvwriter.writerow(select_clause)
            for row in reader:
                # apply WHERE clause if specified
                if where_clause and do_operation(operator,row[column_index],value):
                    selected_row = [row[columns.index(attr)] for attr in select_clause]
                    csvwriter.writerow(selected_row)  
    print('-----------Output written to output.csv-----------')            


def execute(parsed_query):
    # extracting the names of the csv files
    from_clause = parsed_query['FROM']
    print("FROM clause:", from_clause)
    
    # opening the csv files
    with open(from_clause) as csvfile:
        reader = csv.reader(csvfile) #iterator
        columns = next(reader)
        print('The columns in the table are: ',columns)
        execute_select(reader,parsed_query,columns)
        
# WHERE student.class = 'I MTech' ORDER BY student.reg_no ASC
# name, class
def main():
    sql_query = "SELECT name FROM student.csv WHERE reg_no > 5"
    parsed_query = parse_query(sql_query)
    print("Parsed Query:", parsed_query)
    execute(parsed_query)

main()