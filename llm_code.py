import os
import json
import datetime
import re

from pydantic import BaseModel, Field
from typing import Literal, Union, List

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import AIMessage
import tiktoken

from langgraph.graph import StateGraph, END, MessagesState
from langgraph.prebuilt import ToolNode

from tld import get_tld
from urllib.parse import urlparse

from constants import (
    SAFETY_TOKEN_LIMIT,
    OPENAI_API_KEY,
    MODEL_NAME,
    SMALL_MODEL_NAME,
)

from search_code import google_search, download_content, sanitize_text

from prompt_code import update_system_prompt, create_context


llm = ChatOpenAI(model=MODEL_NAME, temperature=0, api_key=OPENAI_API_KEY)
small_llm = ChatOpenAI(model=SMALL_MODEL_NAME, temperature=0, api_key=OPENAI_API_KEY)
token_counters = {}


class Profile(dict):
    """Company Profile Parameters"""

    company: str = ""  # Field(description="Official company name")
    product: str = ""  # Field(description="Official product name")
    url: str = ""  # Field(description="URL leading to the product description")


class SearchResponse(BaseModel):
    """Result of the search query on the internet, containing the title, answer, extract and URL"""

    title: str = Field(description="Title of the web page")
    found: float = Field(
        description="0 if the answer is not found, 0.25 if there are unsatisfying details, 0.5 if the answer is incomplete, 0.75 if the answer is mostly covered, 1.0 if the answer is perfect."
    )
    answer: str = Field(description="Answer to the question")
    extract: str = Field(
        description="Text extract containing the answer provided. 'Not Found' if no extract is available"
    )
    url: str = Field(description="URL to the web page")
    search_queries: List[str] = Field(
        description="List of search queries used to find the answer"
    )


class DefeatResponse(BaseModel):
    """Return a message to the user when the agent couldn't find an answer"""

    answer: str = Field(description="Message to the user")


class AgentState(MessagesState):
    """Final structured response from the agent"""

    final_response: SearchResponse = Field(description="Final response to the user")


@tool
def search_response(
    title: str,
    found: float,
    answer: str,
    extract: str,
    url: str,
    search_queries: List[str],
) -> None:
    """Provide the final answer to the question."""
    pass


@tool
def search_google(query: str, domains: List[str] = None, result_count: int = 3) -> str:
    """Use this to search google.
    The query string is what you are searching for.
    You can specify a list of domains to limit your search.
    modify the result_count to get more or less results, depending on your needs, but keep it as low as possible to save tokens.
    """

    domain_query = ""
    if domains:
        domain_query = " OR ".join([f"site:{domain}" for domain in domains])
        full_query = f"{query} {domain_query} -inurl:pdf"
    else:
        full_query = f"{query} -inurl:pdf"

    result_count = min(max(1, result_count), 10)  # Clamp between 1 and 10
    search_results = google_search(full_query, result_count)

    if not search_results:
        return "No results found"

    answers = []
    unwanted_files = [".txt", ".xlsx", ".docx", ".pptx", ".zip", ".pdf"]
    clean_search_results = [
        r
        for r in search_results
        if not any([ext in r.get("link") for ext in unwanted_files])
    ]
    if len(clean_search_results) == 0:
        return "No results found"

    nb_results = 5
    results = []
    for result in clean_search_results[:nb_results]:
        snippet = download_content(result.get("link"))

        if snippet and num_tokens_from_string(snippet) < SAFETY_TOKEN_LIMIT:
            result["title"] = sanitize_text(result.get("title"))
            result["snippet"] = sanitize_text(snippet)
            results.append(result)
        else:
            print(f"  * Skipping (empty or unsafe) {result.get('link')}")

    if len(results) == 0:
        return "No results found"

    # calculate the total length of the snippets
    lenghts = [num_tokens_from_string(r["snippet"]) for r in results]

    limit = SAFETY_TOKEN_LIMIT
    if sum(lenghts) > SAFETY_TOKEN_LIMIT:
        limit = min(sum(lenghts) // len(results), SAFETY_TOKEN_LIMIT)

    for i, result in enumerate(results):
        title = result.get("title", "")
        snippet = result.get("snippet", "")

        if lenghts[i] > limit:
            snippet = truncate_to_tokens(snippet, limit)
            print(f"    ! truncated to {limit} tokens")

        answers.append(
            f"URL: {result.get('link')}\nTitle: {title}\nExtract: {(snippet)}"
        )

    stringified = "\n---\n".join(answers)
    return stringified


def num_tokens_from_string(string: str, encoding_name: str = "cl100k_base") -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


# function that truncates to x tokens
def truncate_to_tokens(string, tokens):
    encoding = tiktoken.get_encoding("cl100k_base")
    return encoding.decode(encoding.encode(string)[:tokens])


def get_token_counts():
    return token_counters


def count_tokens(response):
    model = response.response_metadata.get("model_name", "unknown")
    if model not in token_counters:
        token_counters[model] = {
            "total": 0,
            "output": 0,
            "input": 0,
            "calls": 0,
        }

    token_counters[model]["total"] += response.usage_metadata["total_tokens"]
    token_counters[model]["output"] += response.usage_metadata["output_tokens"]
    token_counters[model]["input"] += response.usage_metadata["input_tokens"]
    token_counters[model]["calls"] += 1


def reset_token_counts():
    token_counters = {}


# function that extracts the content of a json code block from a string
def extract_json_block(text):
    start = text.find("```json")
    if start == -1:
        return None
    end = text.find("```", start + 7)
    if end == -1:
        return None
    try:
        return json.loads(text[start + 7 : end])
    except Exception as e:
        print("Error parsing JSON block:", e)
        return None


def find_content(parameter, context):

    question = f"""In the following context, list all {parameter} mentioned. Return the list as an array of strings. If none, return an empty array.

Context: 
{context}
"""

    try:
        output = small_llm.invoke(input=question)
        count_tokens(output)
        return extract_json_block(output.content)
    except:
        print("! FAILED:", output)
        print("Trying again with a bigger model")

        output = llm.invoke(input=question)
        count_tokens(output)
        return extract_json_block(output.content)


def build_graph():
    tools = [search_google, search_response]
    model_with_response_tool = llm.bind_tools(tools, tool_choice="any")

    def call_model(state: AgentState):
        """Call the model with the response tool."""
        try:
            response = model_with_response_tool.invoke(state["messages"])
            count_tokens(response)
        except Exception as e:
            print(f"! Error in call_model: {str(e)}")
            response = AIMessage(content="Response not found.")

        return {"messages": [response]}

    def respond(state: AgentState):
        """Respond to the user with the final answer."""
        last_message = state["messages"][-1]
        if (
            last_message.tool_calls
            and last_message.tool_calls[0]["name"] == "search_response"
        ):
            args = last_message.tool_calls[0]["args"]
            for arg in ["title", "answer", "extract", "url"]:
                if arg not in args:
                    args[arg] = ""

            response = SearchResponse(**args)

            return {"final_response": response}
        else:
            print("! No 'search_response' found in the last message.")
            return {"final_response": DefeatResponse(answer="No answer found")}

    def give_up(state: AgentState):
        """Tell the graph to give up."""
        print("! Giving up")
        return {"final_response": DefeatResponse(answer="No answer found")}

    def should_continue(state: AgentState) -> str:
        """Check if the agent should continue or respond to the user."""
        messages = state["messages"]
        last_message = messages[-1]

        attempts = [m for m in messages if hasattr(m, "tool_calls")]
        if len(attempts) > 3 or len(messages) > 20:
            print("! Too many attempts, giving up", len(attempts), len(messages))
            return "giveup"

        if (
            last_message.tool_calls
            and last_message.tool_calls[0]["name"] == "search_response"
        ):
            return "respond"
        else:
            return "continue"

    # Define a new graph
    workflow = StateGraph(AgentState)

    # Define the two nodes we will cycle between
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", ToolNode(tools))
    workflow.add_node("respond", respond)
    workflow.add_node("giveup", give_up)

    # Set the entrypoint as `agent`
    # This means that this node is the first one called
    workflow.set_entry_point("agent")

    # We now add a conditional edge
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "continue": "tools",
            "respond": "respond",
            "giveup": "giveup",
        },
    )

    workflow.add_edge("tools", "agent")
    workflow.add_edge("respond", END)
    workflow.add_edge("giveup", END)

    graph = workflow.compile()

    return graph


def find_answer_to_question(graph, question, previous_answers, profile, domain):
    if not question.get("main", None):
        print("! No query provided")
        return None

    system_prompt = update_system_prompt(profile, domain)
    context = create_context(previous_answers)
    goal = question.get("goal", "Answer the question")
    main = question.get("main")
    expected = question.get("expected")
    full_query = f"Goal: {goal}\nQuestion: {main}"
    if expected:
        full_query += f"\nExpected: {expected}"

    if len(previous_answers) > 0:
        full_query = f"Previous answers:\n{context}\n\n{full_query}"

    print(f"* Q. {question.get('main', '')}")

    initial_state = {
        "messages": [
            ("system", system_prompt),
            ("human", full_query),
        ]
    }

    result = graph.invoke(input=initial_state, config={"recursion_limit": 25})
    answer = result["final_response"]

    return answer


def save_answer_to_cache(
    question, answer, profile, domain, answer_cache, label, followup
):
    all_answers = []

    if os.path.exists(answer_cache):
        with open(answer_cache, "r", encoding="utf-8") as f:
            all_answers = json.load(f)

    if question in [a["question"] for a in all_answers]:
        return

    all_answers.append(
        {
            "company": profile.get("company"),
            "product": profile.get("product"),
            "url": profile.get("url"),
            "domain": domain,
            "question": question,
            "label": label,
            "followup": followup,
            "answer": answer.dict(),
            "timestamp": datetime.datetime.now().isoformat(),
        }
    )

    with open(answer_cache, "w", encoding="utf-8") as f:
        json.dump(all_answers, f, indent=2, ensure_ascii=False)


def load_answer_from_cache(question, answer_cache):
    answers = []
    if os.path.exists(answer_cache):
        with open(answer_cache, "r", encoding="utf-8") as f:
            answers = json.load(f)

    existings = [a for a in answers if a["question"] == question]
    if len(existings) > 0:
        return SearchResponse(**existings[0]["answer"])

    return None


def clean_string(text):
    """Clean company product string by removing spaces and special characters"""
    # Remove special characters and spaces, keep alphanumeric
    cleaned = re.sub(r"[^a-zA-Z0-9]", "", text)

    return cleaned.lower()


def answer_all_questions(
    questions,
    graph,
    profile,
    domain,
):
    print(
        f"Searching the internet for answers about {profile.get('company')} - {profile.get('product')}"
    )
    answers = []
    clean_company = clean_string(profile.get("company", ""))
    clean_product = clean_string(profile.get("product", ""))
    f_company_product = f"{clean_company}_{clean_product}"

    answer_cache = f"assessment_answers_{f_company_product}.json"

    j = 0
    k = 0

    def index_of_question(answers, q):
        for i, a in enumerate(answers):
            if a["question"] == q:
                return i
        return -1

    for i, question in enumerate(questions):
        label = question.get("label", "General")
        k = 0

        answer = load_answer_from_cache(question["main"], answer_cache)

        if not answer:
            answer = find_answer_to_question(graph, question, answers, profile, domain)
            if type(answer) == SearchResponse:
                save_answer_to_cache(
                    question["main"],
                    answer,
                    profile,
                    domain,
                    answer_cache,
                    label,
                    False,
                )

        idx = index_of_question(answers, question["main"])
        if idx == -1:
            answers.append(
                {
                    "question": question["main"],
                    "answer": answer,
                    "label": label,
                    "followup": False,
                }
            )

        if question.get("function") and type(answer) == SearchResponse:
            result = question["function"](
                question.get("parameter", "listed items"), answer.answer
            )
            if type(result) == list:
                for followup in question.get("followup", []):
                    for r in result:
                        k += 1
                        modified_followup = str(followup).replace("PLACEHOLDER", r)
                        followup_answer = load_answer_from_cache(
                            modified_followup, answer_cache
                        )

                        if not followup_answer:
                            followup_answer = find_answer_to_question(
                                graph,
                                {
                                    "goal": "This is a follow up question",
                                    "main": modified_followup,
                                },
                                answers,
                                profile,
                                domain,
                            )

                            if type(followup_answer) == SearchResponse:
                                save_answer_to_cache(
                                    modified_followup,
                                    followup_answer,
                                    profile,
                                    domain,
                                    answer_cache,
                                    label,
                                    True,
                                )

                        idx = index_of_question(answers, modified_followup)

                        if idx == -1:
                            answers.append(
                                {
                                    "question": modified_followup,
                                    "answer": followup_answer,
                                    "label": label,
                                    "followup": True,
                                }
                            )

    return answers


def extract_domain(url):
    """
    Extract the main domain from a URL, handling various formats and TLDs.

    Examples:
        'https://www.example.com' -> 'example.com'
        'http://blog.example.co.uk' -> 'example.co.uk'
        'www.nhk.co.jp' -> 'nhk.co.jp'
    """
    try:
        if not url.startswith(("http://", "https://")):
            url = "http://" + url

        res = get_tld(url, as_object=True)
        return res.fld
    except Exception:
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path
        return domain.split("www.")[-1]


def perform_assessment(questions, profile, graph):
    reset_token_counts()

    domain = extract_domain(profile.get("url"))
    answers = answer_all_questions(questions, graph, profile, domain)

    return answers


def ask_llm(prompt):
    output = llm.invoke(input=prompt)
    count_tokens(output)
    return output.content
