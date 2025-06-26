from langchain_core.prompts import PromptTemplate
from bert_score import score
from rouge_score import rouge_scorer
from google import genai
import json
import os
import time

GEMINI_API_KEY = "my_api_key"
GEMINI_MODEL_NAME = "gemini-2.5-pro-exp-03-25"

# Initialize the Gemini client
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

# Rate limiting variables
MAX_REQUESTS_PER_MINUTE = 10
request_count = 0

# Prompt for hallucination check LLM (https://huggingface.co/PatronusAI/Llama-3-Patronus-Lynx-8B-Instruct-v1.1)
PROMPT = """
Given the following QUESTION, DOCUMENT and ANSWER you must analyze the provided answer and determine whether it is faithful to the contents of the DOCUMENT. The ANSWER must not offer new information beyond the context provided in the DOCUMENT. The ANSWER also must not contradict information provided in the DOCUMENT. Output your final verdict by strictly following this format: "PASS" if the answer is faithful to the DOCUMENT and "FAIL" if the answer is not faithful to the DOCUMENT. Show your reasoning.

--
QUESTION (THIS DOES NOT COUNT AS BACKGROUND INFORMATION):
{question}

--
DOCUMENT:
{context}

--
ANSWER:
{answer}

--

Your output should be in JSON FORMAT with the keys "REASONING" and "SCORE".
{{"REASONING": <your reasoning as bullet points>, "SCORE": <your final score>}}
"""

hallucination_check_prompt = PromptTemplate(
    template=PROMPT,
    input_variables=["question", "context", "answer"]
)

def read_json(file_path):
    dir = os.path.dirname(os.path.abspath(__file__))
    full_file_path = os.path.join(dir, file_path)
    
    with open(full_file_path, "r", encoding="utf-8") as file:
        return json.load(file)

def write_json(file_path, data):
    dir = os.path.dirname(os.path.abspath(__file__))
    full_file_path = os.path.join(dir, file_path)

    with open(full_file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

def split_list(list, n):
    result = []
    for i in range(0, len(list), n):
        result.append(list[i:i+n])
    return result

def extract_data(data):
    all_mistral = []
    all_llama2 = []
    all_refs = []
    all_contents = []
    for item in data:
        n = len(item["summaries_mistral"])
        all_mistral.extend(item["summaries_mistral"])
        all_llama2.extend(item["summaries_llama2"])
        all_refs.extend([item["summary_reference"]] * n)
        all_contents.append([item["content"]])
    return all_mistral, all_llama2, all_refs, all_contents

def calculate_bert_scores(candidates, references):
    P, R, F1 = score(candidates, references, lang="en", verbose=True)
    return P, R, F1

def calculate_rouge_scores(candidates, references):
    rouge = rouge_scorer.RougeScorer(['rouge1', 'rougeL'], use_stemmer=True)
    scores = {'rouge1': [], 'rougeL': []}
    for cand, ref in zip(candidates, references):
        result = rouge.score(ref, cand)
        scores['rouge1'].append(result['rouge1'].fmeasure)
        scores['rougeL'].append(result['rougeL'].fmeasure)
    return scores

def calculate_hallucination_scores(summaries, contents):
    global request_count
    results = []
    summaries_three = split_list(summaries, 3) # For each content, I created 3 summaries
    for content, summaries in zip(contents, summaries_three):
        for summary in summaries:
            formatted_prompt = hallucination_check_prompt.format(
                question="Summarize the terms of service text.",
                context=content,
                answer=summary
            )
            
            if request_count >= MAX_REQUESTS_PER_MINUTE:
                print(f"Rate limit reached. Waiting for 60 seconds.")
                time.sleep(60)
                request_count = 0
            
            try:
                response = gemini_client.models.generate_content(
                    model=GEMINI_MODEL_NAME,
                    contents=formatted_prompt
                )
                request_count += 1
                response_text = response.text.strip()
                
                # Clean up the response text to ensure it is valid JSON
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                
                if json_start >= 0 and json_end > json_start:
                    clean_json = response_text[json_start:json_end]
                    print("Parsed JSON: " + clean_json + "\n")
                    result = json.loads(clean_json)
                    results.append(result["SCORE"] == "PASS")
                else:
                    print("Failed to extract JSON from response: " + response_text)
                    results.append(False)
            except Exception as e:
                print(f"Error during hallucination check: {e}")
                print(f"Response text: {response_text if 'response_text' in locals() else 'Not available'}")
                # Default to False (fail) if there's an error
                results.append(False)
    
    return sum(results) / len(results) if results else 0

def generate_results(bert_results, rouge_results, hallucination_results):
    results = {
        "average_scores": {
            "mistral": {
                "bert_score": {},
                "rouge_score": {},
                "hallucination_score": 0
            },
            "llama2": {
                "bert_score": {},
                "rouge_score": {},
                "hallucination_score": 0
            }
        }
    }
    
    for model in ["mistral", "llama2"]:
        results["average_scores"][model]["bert_score"] = {
            f"avg_{k}": float(getattr(v, 'mean')()) 
            for k, v in zip(["precision", "recall", "f1"], bert_results[model])
        }
        
        results["average_scores"][model]["rouge_score"] = {
            f"avg_{metric}": sum(scores)/len(scores)
            for metric, scores in rouge_results[model].items()
        }
        
        results["average_scores"][model]["hallucination_score"] = hallucination_results[model]
    
    return results

if __name__ == "__main__":
    data = read_json("data/summaries.json")
    
    # Extract data
    mistral_summs, llama2_summs, refs, contents = extract_data(data)
    
    # Calculate BERT and ROUGE scores
    bert_mistral = calculate_bert_scores(mistral_summs, refs)
    bert_llama2 = calculate_bert_scores(llama2_summs, refs)
    rouge_mistral = calculate_rouge_scores(mistral_summs, refs)
    rouge_llama2 = calculate_rouge_scores(llama2_summs, refs)
    
    # Calculate hallucination scores
    hallucination_mistral = calculate_hallucination_scores(mistral_summs, contents)
    hallucination_llama2 = calculate_hallucination_scores(llama2_summs, contents)
    
    # Generate final results
    results = generate_results(
        {"mistral": bert_mistral, "llama2": bert_llama2},
        {"mistral": rouge_mistral, "llama2": rouge_llama2},
        {"mistral": hallucination_mistral, "llama2": hallucination_llama2}
    )
    write_json("data/metrics.json", results)