import csv

def cartesian(file1, file2):
    merged_data = []
    with open(file1, 'r') as file1_csv, open(file2, 'r') as file2_csv:
        reader1 = csv.DictReader(file1_csv)
        reader2 = csv.DictReader(file2_csv)
        
        # Retrieve field names without leading and trailing spaces
        fieldnames1 = [field.strip() for field in reader1.fieldnames]
        fieldnames2 = [field.strip() for field in reader2.fieldnames]
        merged_fieldnames = set(fieldnames1) | set(fieldnames2)
        merged_data.append(merged_fieldnames)
        # Skip headers
        next(reader1)
        next(reader2)
        
        for row1 in reader1:
            file2_csv.seek(0)  # Reset the second file reader to the beginning
            next(reader2)  # Skip the header row in the second file
            for row2 in reader2:
                # Strip leading and trailing spaces from row keys and values
                row1_stripped = {key.strip(): value.strip() for key, value in row1.items()}
                row2_stripped = {key.strip(): value.strip() for key, value in row2.items()}
                
                # Merge dictionaries
                merged_row = {**row1_stripped, **row2_stripped}
                
                # Append merged row to list
                merged_data.append(merged_row)
                
    return merged_data

def natural_join(file1, file2):
    merged_data = []
    with open(file1, 'r') as file1_csv, open(file2, 'r') as file2_csv:
        reader1 = csv.DictReader(file1_csv)
        reader2 = csv.DictReader(file2_csv)

        # Find common columns
        common_columns = set(reader1.fieldnames) & set(reader2.fieldnames)
        print(common_columns)
        
        # Strip leading and trailing spaces from field names
        fieldnames1 = [field.strip() for field in reader1.fieldnames]
        fieldnames2 = [field.strip() for field in reader2.fieldnames]
        
        # Include all columns from both files in merged_fieldnames
        merged_fieldnames = set(fieldnames1) | set(fieldnames2)
        merged_data.append(merged_fieldnames)

        for row1 in reader1:
            file2_csv.seek(0)  # Reset the second file reader to the beginning
            for row2 in reader2:
                if all(row1[col].strip() == row2[col].strip() for col in common_columns):
                    # Strip leading and trailing spaces from row keys and values
                    row1_stripped = {key.strip(): value.strip() for key, value in row1.items()}
                    row2_stripped = {key.strip(): value.strip() for key, value in row2.items()}
                    
                    # Merge dictionaries
                    merged_row = {**row1_stripped, **row2_stripped}
                    merged_data.append(merged_row)
    return merged_data


# natural_join('account.csv', 'customer.csv')
# merged_list = cartesian('account.csv', 'customer.csv')
# # print(merged_list[0])
# print(merged_list)

merged_list = natural_join('account.csv', 'customer.csv')
print(merged_list)
