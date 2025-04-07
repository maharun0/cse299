import csv

# Replace these with your actual file paths
input_file = './dataset/CSE299 - Chatbot Evaluation - Copy of 1000 qna.tsv'
output_file = './output/refined.csv'

with open(input_file, 'r', newline='', encoding='utf-8') as tsvfile, \
     open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
    
    tsv_reader = csv.reader(tsvfile, delimiter='\t')
    csv_writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)

    for row in tsv_reader:
        csv_writer.writerow(row)
