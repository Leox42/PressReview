from Bio import Entrez
from datetime import date
import pandas as pd
import os.path as path
import os
import webbrowser
import urllib.parse
import platform


class PressReviewer:
    def __init__(self, list_of_queries, max_results, email, api_pubmed, html_template):
        self.list_of_queries = list_of_queries
        self.max_results = max_results
        self.email = email
        self.api_pubmed = api_pubmed
        self.html_template = html_template

    def fetch_papers(self):
        for query in self.list_of_queries:
            self.generate_html_from_query(query)

    def fetch_paper_details(self, pubmed_id):
        """
        Fetch and parse paper's detail.

        :param pubmed_id: The paper's ID in Pubmed
        :return: title, authors, abstract, and the updated list of papers
        """
        dict = {}
        handle = Entrez.efetch(db="pubmed", id=pubmed_id, retmode="xml")
        record = Entrez.read(handle)
        handle.close()

        # Initialize variables to store paper details
        title = ""
        authors = ""
        abstract = ""

        # Loop through records and extract information from the first record
        for rec in record['PubmedArticle']:
            if "MedlineCitation" in rec and "Article" in rec["MedlineCitation"]:
                # Extract relevant paper details here (title, authors, abstract, etc.)
                # For example:
                if "ArticleTitle" in rec["MedlineCitation"]["Article"]:
                    title = rec["MedlineCitation"]["Article"]["ArticleTitle"]
                else:
                    title = ''
                if "AuthorList" in rec["MedlineCitation"]["Article"]:
                    for author in rec["MedlineCitation"]["Article"]["AuthorList"]:
                        if 'LastName' in author:
                            lastname = author['LastName']
                        else:
                            lastname = 'NoLastNameFound'
                        if 'Initials' in author:
                            initials = author['Initials']
                        else:
                            initials = 'NoInitialsFound'
                        authors = authors + lastname + ' ' + initials + ','
                else:
                    authors = 'NoAuthorsFound'
                if "Abstract" in rec["MedlineCitation"]["Article"]:
                    abstract_raw = rec["MedlineCitation"]["Article"]["Abstract"]["AbstractText"]
                    if isinstance(abstract_raw, list):
                        for abstract_text in abstract_raw:
                            abstract = abstract + ' ' + abstract_text
                    elif isinstance(abstract_raw, str):
                        abstract = abstract_raw

                else:
                    abstract = ''
                if 'ArticleDate' in rec["MedlineCitation"]["Article"] and len(
                        rec["MedlineCitation"]["Article"]["ArticleDate"]) > 0:
                    paper_date = rec["MedlineCitation"]["Article"]["ArticleDate"][0]
                    paper_date = pd.to_datetime(
                        paper_date['Day'] + '/' + paper_date['Month'] + '/' + paper_date['Year'],
                        dayfirst=True)
                else:
                    paper_date = ''
                if "PublicationTypeList" in rec["MedlineCitation"]["Article"] and len(
                        rec["MedlineCitation"]["Article"]["PublicationTypeList"]) > 0:
                    paper_type = rec["MedlineCitation"]["Article"]["PublicationTypeList"][0]
                else:
                    paper_type = ''

                dict['Title'] = title
                dict['Author'] = authors
                dict['Abstract'] = abstract
                dict['Date'] = paper_date
                dict['Type'] = paper_type
                paper_df = pd.DataFrame([dict])
                break  # Break the loop after extracting from the first record

        return title, authors, abstract, paper_df

    def generate_html_from_query(self, search_query):
        """
        A function that takes as input one query and generates and opens an html page with all the results found.

        :param search_query: a user-defined query
        :param max_results: max number of results to fetch
        :param email: the email of your Pubmed's account
        :param api_pubmed: your Pubmed's api
        :return: void
        """
        # Set up your PubMed API key
        Entrez.email = self.email  # Email address
        Entrez.api_key = self.api_pubmed  # PubMed API key

        # Perform the PubMed search
        handle = Entrez.esearch(db="pubmed", term=search_query, retmax=self.max_results, sort='pub+date')
        record = Entrez.read(handle)
        handle.close()

        # Check if there are search results
        if "IdList" in record:
            # Extract the list of PubMed IDs
            pubmed_ids = record["IdList"]
        else:
            print("No search results found for the query.")
            exit()

        new_papers = pd.DataFrame()

        # Create the newsletter content
        newsletter_content = ""
        for pubmed_id in pubmed_ids:
            title, authors, abstract, paper_df = self.fetch_paper_details(pubmed_id)
            if title and authors and abstract and (len(paper_df) > 0):
                paper_html = "<h2>{}</h2><p>Authors: {}</p><p>{}</p><hr>".format(title, authors, abstract)
                newsletter_content += paper_html
                new_papers = pd.concat([new_papers, paper_df])

        today = date.today()
        # Create an HTML file and write the newsletter content to it
        html_file_path = f"{os.getcwd()}/press_review_output_html/pubmed_newsletter_{search_query.replace(' ', '_')}_{today}.html"
        with open(html_file_path, "w", encoding="utf-8") as html_file:
            html_file.write(self.html_template.format(search_query + ' - ' + str(today), newsletter_content))
        html_file_url = urllib.parse.urljoin('file:', urllib.parse.quote(html_file_path))
        if platform.system() == 'Darwin':
            webbrowser.get('safari').open_new_tab(html_file_url)
        else:
            webbrowser.open_new_tab(html_file_url)

        if path.exists('./press_review_output_csv/' + search_query.replace(' ', '_') + '.csv'):
            csv_library = pd.read_csv('./press_review_output_csv/' + search_query.replace(' ', '_') + '.csv')
            loaded_len = len(csv_library.index)
            csv_library = pd.concat([csv_library, new_papers])
            csv_library.drop_duplicates(subset=['Title'], inplace=True)
            if len(csv_library.index) > loaded_len:
                print(f"{len(csv_library.index) - loaded_len} found for {search_query.replace(' ', '_')} query!")
            csv_library.to_csv('./press_review_output_csv/' + search_query.replace(' ', '_') + '.csv', index=False)
        else:
            new_papers.to_csv('./press_review_output_csv/' + search_query.replace(' ', '_') + '.csv', index=False)

        print(f"Newsletter HTML file generated successfully for query {search_query}!")
