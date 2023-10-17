from press_review import PressReviewer
import yaml

with open('config.yaml', "r") as f:
    yaml_config = yaml.safe_load(f)
list_of_queries = yaml_config['QUERIES']['query_list']
max_results = yaml_config['PARAMS']['max_results']
email = yaml_config['CREDENTIALS']['email']
api_pubmed = yaml_config['CREDENTIALS']['api_pubmed']

with open("review_html_template.html", "r", encoding='utf-8') as f:
    html_template = f.read()

if __name__ == '__main__':
    reviewer = PressReviewer(list_of_queries=list_of_queries,
                             max_results=max_results,
                             email=email,
                             api_pubmed=api_pubmed,
                             html_template=html_template)
    reviewer.fetch_papers()
