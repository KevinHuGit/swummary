from langchain_community.llms import ollama
from langchain_community.document_loaders import TextLoader
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import os
import confluenceAPI

base_url = 'https://swifthackathon.atlassian.net/wiki'
spaces_url = base_url + '/rest/api/content/'

# Initialize the Ollama model
model = ChatOllama(model="phi3:mini")

# def load_articles(directory):
#     articles = []
#     for filename in os.listdir(directory):
#         if filename.endswith(".txt"):
#             loader = TextLoader(os.path.join(directory, filename))
#             document = loader.load()[0]
#             articles.append((filename, document.page_content))
#     return articles

# # Load all articles from a directory
# articles = load_articles("./articles")  # Replace with your directory path

articles = confluenceAPI.query_confluence(base_url)

def summarize_articles(model, articles):
    combined_content = "\n\n".join([f"Article {i+1}:\n{body}" for i, (_,body,_) in enumerate(articles)])
    summarize_prompt = ChatPromptTemplate.from_template(
        "Summarize the following articles together in about 3-4 sentences. DO NOT EXCEED 5 SENTENCES IN YOUR SUMMARY. The summary must be concise, and to the point:\n\n{articles}\n\nSummary:"
    )
    summarize_chain = summarize_prompt | model | StrOutputParser()
    return summarize_chain.invoke({"articles": combined_content})

def compare_summary_to_article(model, summary, article):
    compare_prompt = ChatPromptTemplate.from_template(
        """You are an assistant which rates the similarity of articles on a scale of 0 - 100.

        Summary of all articles: {summary}
        Individual article: {article}

        Please analyze the summary and the individual article and provide a similarity score between 0 and 100, where 0 means completely different and 100 means identical. Print only the score. Do not provide any additional textual information. I only want the the numerical score."""
    )
    compare_chain = compare_prompt | model | StrOutputParser()
    return compare_chain.invoke({"summary": summary, "article": article})

def keyword_search(articles, query):
    query = query.lower()
    keywords = query.split()
    results = []

    for title, content, url in articles:
        content_lower = content.lower()
        score = sum(1 for keyword in keywords if keyword in content_lower)
        if score > 0:
            results.append(title)
    return results

# Example usage of keyword search
def search_articles(query):
    results = keyword_search(articles, query)
    if not results:
        print("No articles found matching the query.")
        return {
            "summary": "",
            "results": []
        }
    else:
        print(f"Found {len(results)} relevant article(s):")
        for title in results:
            print(f"Title: {title}")
        
        select_articles = [article for article in articles if article[0] in results]

        # Summarize all articles together
        overall_summary = summarize_articles(model, select_articles)

        print("Overall Summary of All Articles:")
        print(overall_summary)

        # Compare the overall summary to each individual article
        results = []
        for title, content, url in articles:
            similarity_score = compare_summary_to_article(model, overall_summary, content)
            similarity = 0
            for word in similarity_score.split():
                if word.isdigit():
                    similarity = int(word)
                    break
            print(f"\nSimilarity Score for {title}:")
            print(similarity)
            results.append({
                "title": title,
                "description": content[0:100],
                "url": url,
                "similarity": similarity
            })
            
        return {
            "summary": overall_summary,
            "results": results
        }


