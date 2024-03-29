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
        # remove single quotes from comparison value if present
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


def cartesian(file1,file2):
    data = []
    with open(file1, 'r') as file1_csv, open(file2, 'r') as file2_csv:
        reader1 = csv.reader(file1_csv)
        reader2 = csv.reader(file2_csv)
        header1 = [col.strip() for col in next(reader1)]
        header2 = [col.strip() for col in next(reader2)]
    
        data.append(header1+header2)
        
        for row1 in reader1:
            file2_csv.seek(0)  # reset file2 pointer
            next(reader2)  # skip header row again
            for row2 in reader2:
                merged_row = [value.strip() for value in row1] + [value.strip() for value in row2]
                data.append(merged_row)
    return data

def natural_join(file1, file2):
    data = []

    # read data from file1 and file2
    with open(file1, 'r') as file1_csv:
        reader1 = csv.reader(file1_csv)
        header1 = [col.strip() for col in next(reader1)]
        data1 = [row for row in reader1]
        
    with open(file2, 'r') as file2_csv:
        reader2 = csv.reader(file2_csv)
        header2 = [col.strip() for col in next(reader2)]
        data2 = [row for row in reader2]
        
    # find common columns
    common_columns = set(header1).intersection(header2)

    # include all the columns from both files in columns
    columns = []
    seen = set()  # to keep track of seen columns to avoid duplicates

    # add columns from header1
    for col in header1:
        if col not in seen:
            columns.append(col)
            seen.add(col)

    # add columns from header2 that are not already present
    for col in header2:
        if col not in seen:
            columns.append(col)
            seen.add(col)

    data.append(columns)

    # iterate over data1 and data2 and write to a list
    for row1 in data1:
        for row2 in data2:
            if all(row1[header1.index(col)].strip() == row2[header2.index(col)].strip() for col in common_columns):
                row1 = [value.strip() for value in row1]
                row2 = [value.strip() for value in row2]
                row = row1 + row2
                data.append(row)

    return data

def execute_select(data, parsed_query, columns, join):
    # print(reader)
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
        if join==0:
            if (select_clause[0] == '*' or select_clause[0] == 'ALL'):
                star = 1  
                csvwriter.writerow(columns)
            else:
                star = 0  
                csvwriter.writerow(select_clause)
        else:
            if (select_clause[0] == '*' or select_clause[0] == 'ALL'):
                star = 1  
            else:
                star = 0        

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
            if isinstance(sorted_data[index], str) and sorted_data[index].isdigit():
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


def execute_from(parsed_query):
    
    from_clause = parsed_query['FROM']
    print("FROM clause:", from_clause)
    
    if('NATURAL JOIN' in from_clause):
        csv_filenames = from_clause.split(" NATURAL JOIN ")
        merged_list = natural_join(csv_filenames[0],csv_filenames[1])  
        columns = list(merged_list[0])
        execute_select(merged_list,parsed_query,columns,1)
    elif('CROSS JOIN' in from_clause):
        csv_filenames = from_clause.split(" CROSS JOIN ")
        merged_list = cartesian(csv_filenames[0],csv_filenames[1])  
        columns = list(merged_list[0])
        execute_select(merged_list,parsed_query,columns,1)   
    else:
        with open(from_clause) as csvfile:
            reader = csv.reader(csvfile) 
            columns = next(reader)
            print('The columns in the table are: ',columns)
            data = list(reader)
            execute_select(data,parsed_query,columns,0)
        
def main():
    # give single quotes and no ;
    
    # sql_query = "SELECT * FROM student.csv WHERE percentage >= 80 ORDER BY percentage ASC"
    # sql_query = "SELECT * FROM student.csv ORDER BY percentage DESC"
    # sql_query = "SELECT * FROM student.csv"
    # sql_query = "SELECT name, class FROM student.csv WHERE percentage >= 80"
    sql_query = "SELECT name, class FROM student.csv WHERE class = I MTech"
    # sql_query = "SELECT customer_name, balance FROM customer.csv NATURAL JOIN account.csv WHERE balance >= 100000 ORDER BY balance DESC"
    # sql_query = "SELECT customer_name, account_number FROM customer.csv CROSS JOIN account.csv"
    parsed_query = parse_query(sql_query)
    print("Parsed Query:", parsed_query)
    execute_from(parsed_query)

main()