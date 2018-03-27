"""
boolean_query.py
Dependencies: python 2.7, flask

Students: Modify this code to provide an interface for your Boolean search engine
To start the application:
   >python boolean_query.py
To use the application within a browser, use the url:
   http://127.0.0.1:5000/
"""
from flask import *
from boolean_search import search, get_movie_data, movie_snippet, get_unknown_terms, parse_query

# Create an instance of the flask application within the appropriate namespace (__name__).
# By default, the application will be listening for requests on port 5000.
app = Flask(__name__)

# Welcome page
# Python decorators are used by flask to associate url routes to functions.
@app.route("/")
def query():
    """For top level route ("/"), simply present a query page."""
    return render_template('query_page.html')

# This takes queries and turns them into results
@app.route("/results/<int:page_num>", methods=['POST'])
def results(page_num):
    """Generate a result set for a query and present the 10 results starting with <page_num>."""
    orig_query = request.form['query']           # Get the raw user query
    query, skipped, query_type = parse_query(orig_query)
    # Keep track of any stop words removed from the query to display later.
    # Stop words should be stored in persistent storage when building your index,
    # and loaded into your search engine application when the application is started.
    unknown_terms = get_unknown_terms(query) # Add any unknown terms found in the query to this list.
    if unknown_terms or not query:
        # If your search finds any query terms that are not in the index, add them to unknown_terms and
        # render the error_page.
        print('ERROR PAGE')
        return render_template('error_page.html', unknown_terms=unknown_terms)
    else:
        print(query)
        movie_ids = search(query, query_type)   # Get a list of movie doc_ids that satisfy the query.
        # render the results page
        num_hits = len(movie_ids)               # Save the number of hits to display later
        movie_ids = movie_ids[((page_num-1)*10):(page_num*10)]  # Limit of 10 results per page
        movie_results = map(movie_snippet, movie_ids, [query]*len(movie_ids))   # Get movie snippets: title, abstract, etc.
        return render_template('results_page.html', orig_query=orig_query, results=movie_results, srpn=page_num,
                               len=len(movie_ids), skipped_words=skipped, total_hits=num_hits)

#Process requests for movie_data pages
@app.route('/movie_data/<film_id>')
def movie_data(film_id):
    """Given the doc_id for a film, present the title and text (optionally structured fields as well)
    for the movie."""
    data = get_movie_data(film_id)     #Get all of the info for a single movie
    return render_template('doc_data_page.html', data=data)

# If this module is called in the main namespace, invoke app.run()
if __name__ == "__main__":
    app.run()
