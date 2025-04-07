import pandas as pd
import os
from deepeval.metrics import (
    FaithfulnessMetric,
    AnswerRelevancyMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    ContextualRelevancyMetric,
)
from deepeval.test_case import LLMTestCase

# File paths
file_path = './output/refined.csv'
output_file = './output/metrics_results.csv'

# Load dataset
df = pd.read_csv(file_path)

# Load existing results if available
if os.path.exists(output_file):
    existing_results = pd.read_csv(output_file)
    processed_keys = set(
        zip(
            existing_results['question'].astype(str).str.strip(),
            existing_results['expected_answer'].astype(str).str.strip(),
            existing_results['bot_answer'].astype(str).str.strip()
        )
    )
else:
    processed_keys = set()

# Initialize metrics
faithfulness_metric = FaithfulnessMetric(threshold=0.5)
answer_relevancy_metric = AnswerRelevancyMetric(threshold=0.5)
contextual_precision_metric = ContextualPrecisionMetric(threshold=0.5)
contextual_recall_metric = ContextualRecallMetric(threshold=0.5)
contextual_relevancy_metric = ContextualRelevancyMetric(threshold=0.5)

# Function to evaluate metrics for a single row
def evaluate_row(row):
    try:
        input_text = str(row['question']).strip()
        expected_answer = str(row['expected_answer']).strip()
        bot_answer = str(row['bot_answer']).strip()
        retrieval_context = [expected_answer]

        if not input_text or not expected_answer or not bot_answer:
            raise ValueError("Missing or invalid input data")

        test_case = LLMTestCase(
            input=input_text,
            actual_output=bot_answer,
            expected_output=expected_answer,
            retrieval_context=retrieval_context
        )

        # Metric results
        faithfulness_result = faithfulness_metric.measure(test_case)
        answer_relevancy_result = answer_relevancy_metric.measure(test_case)
        contextual_precision_result = contextual_precision_metric.measure(test_case)
        contextual_recall_result = contextual_recall_metric.measure(test_case)
        contextual_relevancy_result = contextual_relevancy_metric.measure(test_case)

        def get_score(result, metric_name):
            if isinstance(result, float):
                return result
            elif hasattr(result, 'score'):
                return result.score
            else:
                raise ValueError(f"Unexpected result type from {metric_name}: {type(result)}")

        return {
            'question': input_text,
            'expected_answer': expected_answer,
            'bot_answer': bot_answer,
            'faithfulness_result': get_score(faithfulness_result, "FaithfulnessMetric"),
            'answer_relevancy_result': get_score(answer_relevancy_result, "AnswerRelevancyMetric"),
            'contextual_precision_result': get_score(contextual_precision_result, "ContextualPrecisionMetric"),
            'contextual_recall_result': get_score(contextual_recall_result, "ContextualRecallMetric"),
            'contextual_relevancy_result': get_score(contextual_relevancy_result, "ContextualRelevancyMetric"),
        }

    except Exception as e:
        print(f"Error evaluating row: {row}")
        print(f"Error details: {e}")
        return None

# Process each row and skip if already evaluated
for idx, row in df.iterrows():
    key = (
        str(row['question']).strip(),
        str(row['expected_answer']).strip(),
        str(row['bot_answer']).strip()
    )

    if key in processed_keys:
        print(f"Skipping row {idx + 1}/{len(df)} (already evaluated).")
        continue

    print(f"Evaluating row {idx + 1}/{len(df)}...")
    metrics = evaluate_row(row)

    if metrics is None:
        print("Skipping row due to evaluation error.")
        continue

    # Save metrics to CSV immediately with double quotes
    pd.DataFrame([metrics]).to_csv(output_file, mode='a', index=False, quoting=1, header=not os.path.exists(output_file))

print("Metrics evaluation completed.")