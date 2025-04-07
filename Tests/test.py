import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import confusion_matrix
from nltk.translate.bleu_score import sentence_bleu
from rouge_score import rouge_scorer
import numpy as np

# Replace this with your actual file path
file_path = './output/refined.csv'

# Load data from the CSV file
df = pd.read_csv(file_path)

# Function to calculate BLEU Score
def calculate_bleu(expected_answer, bot_answer):
    reference = expected_answer.split()
    hypothesis = bot_answer.split()
    return sentence_bleu([reference], hypothesis)

# Function to calculate ROUGE Score
def calculate_rouge(expected_answer, bot_answer):
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    scores = scorer.score(expected_answer, bot_answer)
    return scores

# Function to calculate Exact Match
def calculate_exact_match(expected_answer, bot_answer):
    return expected_answer.lower() == bot_answer.lower()

# Function to calculate Hit Rate
def calculate_hit_rate(expected_answer, bot_answer, relevant_answers):
    return any(answer.lower() in bot_answer.lower() for answer in relevant_answers)

# Function to compare answers and return metrics
def evaluate_metrics(df):
    bleu_scores = []
    rouge_scores = []
    exact_matches = []
    hit_rates = []
    
    relevant_answers = df['expected_answer'].unique()  # Assuming unique answers in expected_answer are relevant
    
    for idx, row in df.iterrows():
        expected_answer = row['expected_answer']
        bot_answer = row['bot_answer']
        
        # BLEU Score
        bleu_score = calculate_bleu(expected_answer, bot_answer)
        bleu_scores.append(bleu_score)
        
        # ROUGE Score
        rouge_score = calculate_rouge(expected_answer, bot_answer)
        rouge_scores.append(rouge_score)
        
        # Exact Match
        exact_match = calculate_exact_match(expected_answer, bot_answer)
        exact_matches.append(exact_match)
        
        # Hit Rate
        hit_rate = calculate_hit_rate(expected_answer, bot_answer, relevant_answers)
        hit_rates.append(hit_rate)
    
    # Calculate the accuracy metrics
    accuracy = sum(exact_matches) / len(exact_matches)
    precision = precision_score(exact_matches, [True] * len(exact_matches), average='binary')
    recall = recall_score(exact_matches, [True] * len(exact_matches), average='binary')
    f1 = f1_score(exact_matches, [True] * len(exact_matches), average='binary')

    # Confusion Matrix
    cm = confusion_matrix(exact_matches, [True] * len(exact_matches))
    
    # Calculate BLEU and ROUGE scores
    avg_bleu = np.mean(bleu_scores)
    avg_rouge1 = np.mean([score['rouge1'].fmeasure for score in rouge_scores])
    avg_rouge2 = np.mean([score['rouge2'].fmeasure for score in rouge_scores])
    avg_rougeL = np.mean([score['rougeL'].fmeasure for score in rouge_scores])

    # Calculate Hit Rate
    avg_hit_rate = np.mean(hit_rates)
    
    return accuracy, precision, recall, f1, cm, avg_bleu, avg_rouge1, avg_rouge2, avg_rougeL, avg_hit_rate

# Run the evaluation function
accuracy, precision, recall, f1, cm, avg_bleu, avg_rouge1, avg_rouge2, avg_rougeL, avg_hit_rate = evaluate_metrics(df)

# Print the results
print(f"Accuracy: {accuracy}")
print(f"Precision: {precision}")
print(f"Recall: {recall}")
print(f"F1 Score: {f1}")
print(f"Confusion Matrix:\n{cm}")
print(f"Average BLEU Score: {avg_bleu}")
print(f"Average ROUGE-1 Score: {avg_rouge1}")
print(f"Average ROUGE-2 Score: {avg_rouge2}")
print(f"Average ROUGE-L Score: {avg_rougeL}")
print(f"Hit Rate: {avg_hit_rate}")
