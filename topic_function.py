import requests
from bs4 import BeautifulSoup
import pandas as pd

topics_url = 'https://github.com/topics'


# Get HTML Parsed data from the given URL;
def get_topics_page(topics_url):
    # TODO - add comments
    response = requests.get(topics_url)
    if response.status_code != 200:
        raise Exception('Failed to load page {}'.format(topics_url))
    doc = BeautifulSoup(response.text, 'html.parser')
    return doc


# Get the Titles of repositories;
def get_topic_titles(doc):
    selection_class = 'f3 lh-condensed mb-0 mt-1 Link--primary'
    topic_title_tags = doc.find_all('p', {'class': selection_class})
    topic_titles = []
    for tag in topic_title_tags:
        topic_titles.append(tag.text)
    return topic_titles


# Get the Titles of repositories;
def get_topic_links(doc):
    selection_class = 'no-underline flex-1 d-flex flex-column'
    topic_title_links = doc.find_all('a', {'class': selection_class})
    base_url = 'https://github.com'
    topic_links = []
    for tag in topic_title_links:
        topic_links.append(base_url + tag["href"])
    return topic_links


# Get the Description of repositories;
def get_topic_descs(doc):
    desc_selector = 'f5 color-fg-muted mb-0 mt-1'
    topic_desc_tags = doc.find_all('p', {'class': desc_selector})
    topic_descs = []
    for tag in topic_desc_tags:
        topic_descs.append(tag.text.strip())
    return topic_descs


# Get the username, repository name and number of stars;
def get_details_per_topic(link, title_name):
    response = requests.get(link)
    if response.status_code != 200:
        raise Exception('Failed to load page {}'.format(link))
    topic_doc = BeautifulSoup(response.text, 'html.parser')
    take = topic_doc.prettify()

    # Authors list and his/her main Topic;
    selection_class = 'f3 color-fg-muted text-normal lh-condensed'
    topic_titles_h3 = topic_doc.find_all('h3', {'class': selection_class})

    title_authors_list = []
    title_subject_list = []
    for each_title in topic_titles_h3:
        topic_title_links = each_title.find_all('a')
        title_author = topic_title_links[0].text.strip()
        title_subject = topic_title_links[1].text.strip()
        title_authors_list.append(title_author)
        title_subject_list.append(title_subject)

    # Get the Number of stars for each of the topic;
    star_count_list = []
    selection_class = 'repo-stars-counter-star'
    star_data_list = topic_doc.find_all('span', {'id': selection_class})
    for each_data in star_data_list:
        count_data = float(each_data.text.strip().replace('k', ''))
        count_d = float(count_data * 1000)
        star_count_list.append(count_d)

    # Dictionary from the above Data;
    sub_topic_dict = {
        "Author": title_authors_list,
        "Subject Title": title_subject_list,
        "Stars Count": star_count_list
    }

    # To Pandas Dataframe;
    pd_frame = pd.DataFrame.from_dict(sub_topic_dict)

    # Write out the Main Topics and details to a CSV;
    csvfile = 'G:/Python_Projects/Data_Science/Github_Topics_Scraping/Outputs/'
    csvfile = csvfile + title_name + ".csv"
    pd_frame.to_csv(csvfile, index=False)


# Main function of scraping the data from GIT-HUB;
def scrape_topics_to_csv(csvfile):
    # HTML Parsed data from the URL;
    topic_doc = get_topics_page(topics_url)
    # Titles in the page;
    titles = get_topic_titles(topic_doc)
    topic_links = get_topic_links(topic_doc)
    topic_descs = get_topic_descs(topic_doc)

    # Dictionary from the above Data;
    topic_dict = {
        "Titles": titles,
        "Description": topic_descs,
        "URL": topic_links
    }

    # To Pandas Dataframe;
    pd_frame = pd.DataFrame.from_dict(topic_dict)

    # Write out the Main Topics and details to a CSV;
    pd_frame.to_csv(csvfile, index=False)

    # For each Main Topic get the top authors, subject and number of stars;
    for index in range(len(titles)):
        title_name = titles[index]
        title_link = topic_links[index]
        get_details_per_topic(title_link, title_name)
