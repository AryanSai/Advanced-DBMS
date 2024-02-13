import csv

# path = 'student.csv'

# with open(path, newline='') as csvfile:
#     reader = csv.reader(csvfile)
    
#     #extract the column names
#     fields = next(reader)
#     print(fields)
    
#     #print the line number----starts with 1
#     print(reader.line_num)
        
#     for row in reader: #each row is a list : The ', ' is the separator that is placed between list elements
#         print(', '.join(row))

# print('saoooooooooooooooooo')
# rows = []      
# with open(path, newline='') as csvfile:
#     reader = csv.DictReader(csvfile)
#     for row in reader:
#         rows.append(row)
#         print(row['name'], row['class']) #to access a specific column in each row
# # print(rows)

# # with open('output.csv', 'w') as csvfile:
# #     csvwriter = csv.writer(csvfile)
# #     csvwriter.writerows(rows)

# # Writing to output.csv
# with open('output.csv', 'w', newline='') as csvfile:
#     csvwriter = csv.DictWriter(csvfile, fieldnames=fields)
    
#     # Write header
#     csvwriter.writeheader()
    
#     # Write rows
#     csvwriter.writerows(rows)


# # Writing to output.csv with specific fields
# with open('output2.csv', 'w', newline='') as csvfile:
#     fieldnames = ['name', 'class']  # Include only the fields you want to write
#     csvwriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
#     # Write header
#     csvwriter.writeheader()
    
#     # Write rows with specific fields
#     for row in rows:
#         # Create a new dictionary containing only the desired fields
#         selected_fields = {fieldname: row[fieldname] for fieldname in fieldnames}
#         csvwriter.writerow(selected_fields)
        
# print('newwwwwwwwwwwwwwwwwww')
# column='name'
# value='John Doe'
# with open(path, newline='') as csvfile:
#     reader = csv.DictReader(csvfile)
#     for row in reader:
#         if(row[column]==value):
#            print(row['name'], row['class']) #to access a specific column in each row





# Opening the CSV file
with open('student.csv') as csvfile:
    reader = csv.reader(csvfile)  # Iterator

    # Extracting column names from the first row
    columns = next(reader)
    print('The columns in the table are:', columns)

    # Storing the data rows
    data = []
    for row in reader:
        data.append(row)

# Printing the stored data
print('The data in the CSV file:')
for row in data:
    print(row)
