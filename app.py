from flask import Flask, render_template, request, redirect
from main import search_articles
app = Flask(__name__)

@app.route("/")
def landing_page():
    return render_template('index.html')

results = []
summary = ""
last_search_value = ""
@app.route("/search", methods=('GET', 'POST'))
def search_page():
    global results
    global summary
    global last_search_value

    if request.method == 'GET':
        return render_template("search_page.html", results = results, summary = summary, last_search_value = last_search_value)
    elif request.method == 'POST':
        search_input = request.form['search']
        print(request.form)
        print(search_input)
        
        # DO SEARCH
        search_results = search_articles(search_input)
        
        pre_sorted_results = search_results['results']
        results = sorted(pre_sorted_results, key=lambda x: x['similarity'], reverse=True)
        summary = search_results['summary']
        
        last_search_value = search_input
        return redirect(request.url)
    return render_template("search_page.html", results = results, summary = summary, last_search_value = last_search_value)