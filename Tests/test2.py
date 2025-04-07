import pandas as pd

# Load the CSV file
df = pd.read_csv("./output/metrics_results.csv")  # replace with your actual file name or path

# List of score columns
score_columns = [
    "faithfulness_result",
    "answer_relevancy_result",
    "contextual_precision_result",
    "contextual_recall_result",
    "contextual_relevancy_result"
]

# Convert columns to float (in case they are strings)
df[score_columns] = df[score_columns].astype(float)

# Calculate overall average for each score column
overall_scores = df[score_columns].mean()

# Print the results
print("Overall Scores:")
print(overall_scores)
