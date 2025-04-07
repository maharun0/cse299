import csv

input_file = './dataset/chemistry.csv'
output_file = './dataset/chemistry_cleaned.csv'

# Step 1: Read all rows and detect valid ones
with open(input_file, 'r', encoding='utf-8') as infile:
    reader = csv.reader(infile, delimiter=';')
    rows = list(reader)

# Step 2: Get number of columns from header
expected_cols = len(rows[0])

# Step 3: Keep only rows with the correct number of columns
clean_rows = [row for row in rows if len(row) == expected_cols]

# Step 4: Save cleaned data with quoted fields and , as separator
with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
    writer = csv.writer(outfile, delimiter=',', quoting=csv.QUOTE_ALL)
    writer.writerows(clean_rows)
