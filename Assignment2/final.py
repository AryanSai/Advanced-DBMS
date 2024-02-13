import csv, re

def parse_query(query):
    parsed_query = {}
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
    pattern = r'(\w+)\s*(=|<|>|<=|>=|!=)\s*(\'?\w+\s?\w+\'?|\d+)'
    match = re.search(pattern, where_clause)
    if match:
        column_name = match.group(1)
        operator = match.group(2)
        comparison_value = match.group(3)
        # Remove single quotes from comparison value if present
        comparison_value = comparison_value.strip("'")
        return column_name, operator, comparison_value
    else:
        return None, None, None


def do_operation(operator, row_value, value):
    if isinstance(row_value, str) and row_value.isdigit() and isinstance(value, str) and value.isdigit():
        row_value = int(row_value)
        value = int(value)
    if operator == '=':
        return row_value == value
    elif operator == '>':
        return row_value > value
    elif operator == '<':
        return row_value < value
    elif operator == '>=':
        return row_value >= value
    elif operator == '<=':
        return row_value <= value

def execute_select(reader, parsed_query, columns):
    select_clause = parsed_query['SELECT']
    print("SELECT clause:", select_clause)
    where_clause = parsed_query.get('WHERE')  # get WHERE clause from parsed query
    print("WHERE clause:", where_clause)
    if where_clause:
        column, operator, value = parse_where_condition(where_clause)
        # get the index of the column specified in the WHERE clause
        column_index = columns.index(column)
    
    with open('output.csv', 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        # writing the header
        if select_clause[0] == '*' or select_clause[0] == 'ALL':
            star = 1  
            csvwriter.writerow(columns)
        else:
            star = 0  
            csvwriter.writerow(select_clause)
        
        # storing the data in a list
        data = list(reader)

        # apply WHERE clause if specified
        sorted_data = []
        if where_clause:
            for row in data:
                if do_operation(operator, row[column_index], value):
                    sorted_data.append(row)
        else:
            sorted_data = data
        
        order_by_clause = parsed_query.get('ORDER BY')
        if order_by_clause:
            column_name = order_by_clause.split()[0]
            reverse = order_by_clause.split()[-1].upper() == 'DESC'
            index = columns.index(column_name)
            if isinstance(sorted_data[0][index], str) and sorted_data[0][index].isdigit():
                sorted_data.sort(key=lambda x: int(x[index]), reverse=reverse)
            else:
                sorted_data.sort(key=lambda x: x[index], reverse=reverse)

        # writing the data
        if star:
            csvwriter.writerows(sorted_data)
        else:
            for row in sorted_data:
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
        
# name, class
def main():
    # sql_query = "SELECT * FROM student.csv WHERE percentage >= 80 ORDER BY percentage ASC"
    # sql_query = "SELECT * FROM student.csv"
    
    # give single quotes and no ;
    sql_query = "SELECT * FROM student.csv WHERE class = 'I MTech' ORDER BY percentage"
    parsed_query = parse_query(sql_query)
    print("Parsed Query:", parsed_query)
    execute(parsed_query)

main()