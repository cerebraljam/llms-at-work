import json
import datetime


def update_system_prompt(profile, domain):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    system_prompt = f"""
You are an expert at extracting compliance-related answers from web page content. You are supporting a security team to retrieve information about SaaS providers and their services. 

The team cares about Confidentiality, Integrity, and Availability, as well as Privacy and that SaaS will not be pressured by autocratic governments to collaborate against our company's interest.

The team is trying to assess the security posture of the SaaS provider. 

Briefly answer questions. Focus on technical details. Do not include marketing fluff in your answers. 

For Yes / No / Partially questions, start answering with 'Yes', 'No' or 'Partial', then provide details. Mention if the answer can't clearly be found.

For categorization questions, provide the category and a brief explanation. It is okay to answer based on previously answered questions if the answer can't be found on the company's web pages.

You have access to two tools:
1. 'search_google' which you can use to search for information.
2. 'search_response' which you should use to provide your final answer when you have found the necessary information.

Remember to use 'search_response' to report your final answer.

Today is: {today} 
Company: {profile.get('company')}
Product: {profile.get('product')}
Official company domain: {domain}

"""

    return system_prompt


# transform previous answers into a string that can be inserted in the system prompt as context
def create_context(answers):
    context = ""
    if len(answers) == 0:
        return "No previous answers"

    for row in answers:
        context += f"Q: {row['question']}\nA: {row['answer'].answer}\n\n"
    return context


def make_summary_prompt(answers, profile):
    context = ""
    for answer in answers:
        context += f"\nQ: {answer['question']}\nA: {answer.get('answer').answer}\nConfidence in the answer: {answer.get('answer').found * 100}%\n\n"

    summary_prompt = f"""You are an expert at writing executive summary for security assessment for SaaS products.

Your task is to answer the following questions in as few words as possible, but yet being informative stakeholders. If you need to provide more context, you can provide a brief explanation.
If multiple items must be listed, use bullet points.
When mentioning about risks, please provide a brief explanation of the risk and the potential impact.

Company: {profile.get('company')}
Product: {profile.get('product')}

Context:
```
CONTEXT
```

Please answer the following questions:

Goal of the product, why are we deploying it, how will it help us solve issues we are facing?

What are the laws and regulations that this company is compliant with?

What are the compliance standards that this company is compliant with?

What are the security standards that the company is following?

What kind of data this product is meant to process or store?

Are there risks that were highlighted that the Risk and Security team should be made aware of?

Are there any countermeasures that should be implemented to mitigate risks of using this product?
"""
    return summary_prompt.replace("CONTEXT", context)
