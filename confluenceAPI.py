from atlassian import Confluence
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv, dotenv_values 

load_dotenv() 

base_url = 'https://swifthackathon.atlassian.net/wiki'
spaces_url = base_url + '/rest/api/content/'
# page_url = spaces_url + '196742' + '?expand=body.storage'


def remove_html_tags(text):
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text()

def callAPI(url):
    headers = {
        'Accept' : 'application/json',
        'Authorization' : f'Bearer {os.getenv("API_TOKEN")}'
    }
    response = requests.get(url, headers=headers)
    return response.json()

def query_confluence(base_url):
    ret_list = []

    space_output = callAPI(spaces_url)
    for result in space_output['results']:
        page_url = spaces_url + result['id'] + '?expand=body.storage'
        page_output = callAPI(page_url)

        # extract info for each page
        title = page_output['title'] 
        body_with_html = page_output['body']['storage']['value']
        body_sanitized = remove_html_tags(body_with_html)
        web_url = base_url + page_output['_links']['webui']

        # print("web_url: " + web_url)
        # print("\n")

        ret_list.append((title,body_sanitized,web_url))
        
        # print(title)
        # print(body_sanitized)
        # print("\n")

    return ret_list

