import os
import datetime
import json

import requests
from requests.exceptions import RequestException
from urllib.parse import quote_plus

from llm_code import extract_domain, get_token_counts
from constants import LLM_MODEL_PRICES


def summary_markdown(summary, profile):

    return (
        f"""# Executive Summary Report
* Company: {profile.get('company')}
* Product: {profile.get('product')}
* URL: {profile.get('url')}
* Date: {datetime.datetime.now().strftime("%Y-%m-%d")}


"""
        + summary
    )


# Function that takes the answers and produce a report in markdown
def report_markdown(answers, profile):

    today = datetime.datetime.now().strftime("%Y-%m-%d")
    full_report = f"""# Report for {profile.get('company')} {profile.get('product')} ({today})

URL: {profile.get('url')}
    
## Answers
"""
    j = 0
    k = 0
    for i, answer in enumerate(answers):
        if not answer.get("followup", False):
            k = 0
            full_report += f"""
###  {1+i-j} ({answer['label']}) {answer['question']}
Answer ({answer['answer'].found *100}% confidence): {answer['answer'].answer}
"""
            if "url" in answer["answer"]:
                full_report += f"""
[Read more]({answer['answer'].url}) {answer['answer'].url}
"""
        else:
            j += 1
            k += 1
            full_report += f"""
####  {1+i-j}.{k} ({answer['label']}) {answer['question']}
Answer ({answer['answer'].found * 100}% confidence): {answer['answer'].answer}
"""
            if "url" in answer["answer"]:
                full_report += f"""

[Read more]({answer['answer'].url}) {answer['answer'].url}
"""
    return full_report


def request_for_improvement(answer, profile):
    """
    This code will perform a requests.get to domain/compliance.txt and provide the question that couldn't be answered as a parameter.
    """

    domain = extract_domain(profile["url"])

    if domain not in answer["answer"].url:
        print("* This answer is not from the vendor's website")
        return None

    requested_improvements = {}
    if os.path.exists("requested_improvements.json"):
        with open("requested_improvements.json", "r") as f:
            requested_improvements = json.load(f)

    headers = {
        "User-Agent": "Mercari Vendor Check Agent/1.0 (+https://engineering.mercari.com/en/blog/entry/20241215-llms-at-work)"
    }

    url = f"https://{domain}/compliance.txt"
    parameters = {"question": answer["question"]}

    if domain in requested_improvements:
        if answer["question"] in requested_improvements[domain]:
            return "Already requested"

    try:
        encoded_parameters = "&".join(
            [f"{k}={quote_plus(str(v))}" for k, v in parameters.items()]
        )
        print(f"Requesting '{url}?{encoded_parameters}'")

        response = requests.get(url, params=parameters)

        if domain not in requested_improvements:
            requested_improvements[domain] = []

        requested_improvements[domain].append(answer["question"])
        with open("requested_improvements.json", "w") as f:
            json.dump(requested_improvements, f, indent=2, ensure_ascii=False)

        return response.text
    except RequestException as e:
        return None


def model_price(model):
    # example: gpt-4o-2024-05-13
    sections = model.split("-")

    for i in range(len(sections) - 1, 0, -1):
        model_name = "-".join(sections[:i])
        if model_name in LLM_MODEL_PRICES:
            break

    if model_name not in LLM_MODEL_PRICES:
        model_name = list(LLM_MODEL_PRICES.keys())[0]

    return LLM_MODEL_PRICES[model_name]


def calculate_token_counts(profile):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    token_report = get_token_counts()

    current_token_report = {
        "company": profile["company"],
        "product": profile["product"],
        "product_url": profile["url"],
        "date": today,
        "total_costs": 0,
        "models": [],
    }
    for model in token_report.keys():
        price = model_price(model)
        price_input = price["input"] * token_report[model]["input"] / 1000000
        price_output = price["output"] * token_report[model]["output"] / 1000000
        total_price = price_input + price_output
        current_token_report["total_costs"] += total_price

        current_token_report["models"].append(
            {
                "model": model,
                "calls": token_report[model]["calls"],
                "input": token_report[model]["input"],
                "input_price": price_input,
                "output": token_report[model]["output"],
                "output_price": price_output,
                "total": token_report[model]["total"],
                "total_price": total_price,
            }
        )
    return current_token_report


def token_count_markdown(current_token_report):
    token_report = current_token_report
    token_report_markdown = f"""# Token Usage Report
* Total costs: {token_report['total_costs']:0.2f}$
"""
    for model in token_report["models"]:
        token_report_markdown += f"""
## Model: {model['model']}
* Total calls: {model['calls']}
* Total tokens: {model['total']} ({model['total_price']:0.2f}$)
* Input tokens: {model['input']} ({model['input_price']:0.2f}$)
* Output tokens: {model['output']} ({model['output_price']:0.2f}$)
"""
    return token_report_markdown


def report_confidence(answers, profile):
    trusts = []
    confidences = []
    improvements = []
    domain = extract_domain(profile.get("url"))

    for i, answer in enumerate(answers):
        confidence = answer.get("answer").found
        confidences.append(confidence)
        if domain in answer["answer"].url:
            trusts.append(answer["answer"].url)

        if answer.get("answer").found < 0.5:
            improvements.append(answer)

    report = f"""# Confidence Report
* Percentage of answers collected from the vendor's web pages: {len(trusts)/len(answers)*100:0.2f}%
* Average confidence score: {sum(confidences)/len(confidences)*100:.0f}%
* Number of answers with low confidence scores: {len(improvements)}

Answers with low confidence scores:

"""
    for i, answer in enumerate(answers):
        if answer.get("answer").found < 0.5:
            report += f"""{i+1}. ({answer.get('answer').found * 100:.0f}% confidence) {answer['question']}\n"""

    return report, improvements
