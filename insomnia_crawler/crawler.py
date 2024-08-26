import requests
from bs4 import BeautifulSoup
import os
import json
import tqdm


def dominant_language(text):
    """
    Checks whether the majority of the letters in the input text are in the greek or the latin script

    Args:
        text (str): The input text

    Returns:
        script (str): The dominant script
    """
    # Filter out non-letter characters
    valid_characters = [char for char in text if char.isalpha()]
    
    # Count Greek and English letters
    greek_count = sum(1 for char in valid_characters if '\u0370' <= char <= '\u03FF' or '\u1F00' <= char <= '\u1FFF')
    english_count = sum(1 for char in valid_characters if '\u0041' <= char <= '\u005A' or '\u0061' <= char <= '\u007A')
    
    script = "greek" if greek_count >= english_count else "latin"
    return script

class InsomniaCrawler:

    """
    A class that crawls the Insomnia.gr forums and extracts the comments of the users 
    along with the date and time


    Attributes:
        data_folder (str): The folder where the data will be stored
        base_url (str): The base url of the Insomnia.gr forums
    
    """

    def __init__(self, data_folder = None):
        self.data_folder = data_folder
        self.base_url = 'https://www.insomnia.gr/forums/'

    def crawl(self):

        """
        Loads the forums and calls the crawl_forum method to crawl each forum
        It stores the data of each forum in a separate json file
        """

        try: 
            base_page = requests.get(self.base_url)
            base_page_soup = BeautifulSoup(base_page.content, 'html.parser')

            # Get the urls of the forums
            forums = base_page_soup.find_all('a', class_='insCategory-item')

        except requests.exceptions.RequestException as e:
            print("Problem connecting and parsing the base page:", str(e))
            return 

        # Iterate over the forums
        for forum in forums:
            forum_name = forum.text
            print("crawling forum: ", forum_name)
            forum_data = self.crawl_forum(forum)

            with open(os.path.join(self.data_folder, f"{forum_name}.json"), "w") as f:
                json.dump(forum_data, f)
    
    def crawl_forum(self, forum):
        """
        Loads the forum pages and calls the crawl_post method to crawl each post
        It returns the data of the forum

        Args: forum (bs4.element.Tag): The forum element

        Returns: forum_data (list): The data of the forum
        """
        # Get the html of the forum
        forum_thread = requests.get(forum['href'])
        forum_thread_soup = BeautifulSoup(forum_thread.content, 'html.parser')

        # Get the number of pages in the forum
        num_forum_pages = forum_thread_soup.find('li', class_='ipsPagination_pageJump').find('a').text
        num_forum_pages = int(num_forum_pages.split(" ")[-2])

        # Iterate over the pages in reverse order

        forum_data = []

        # Iterate over the forum pages
        for forum_page in tqdm.tqdm(range(num_forum_pages, 0, -1)[:3]):

            # Get the html of the specific forum page
            try:
                forum_thread_page = requests.get(forum['href'] + 'page/' + str(forum_page))
                forum_thread_page_soup = BeautifulSoup(forum_thread_page.content, 'html.parser')
                posts = forum_thread_page_soup.find_all('div', class_='ipsDataItem_main')

            except requests.exceptions.RequestException as e:
                print("Problem connecting and parsing the forum page:", str(e))
                continue

           

            posts_data = []

             # Iterate over the posts in the forum page
            for post in posts:
                
                # Crawl data of each post
                post_data = self.crawl_post(post)
                posts_data.extend(post_data)

            forum_data.extend(posts_data)

        return forum_data
    
    def crawl_post(self, post):
        """ 
        Crawls the data of a post

        Args: post (bs4.element.Tag): The post element

        Returns: post_data (dict): The data of the post
        """


        post_url = post.find('h4').find('a')['href']

        try:
            post_soup = requests.get(post_url)
            post_soup = BeautifulSoup(post_soup.content, 'html.parser')

            num_post_pages = post_soup.find('li', class_='ipsPagination_pageJump')
        except requests.exceptions.RequestException as e:
            print("Problem connecting and parsing the post page:", str(e))
            return 

        # If the number of pages is not visible, it means that there is only one page
        if(num_post_pages is None):
            num_post_pages = 1
        else:
            num_post_pages = num_post_pages.find('a').text
            num_post_pages = int(num_post_pages.split(" ")[-2])

        comments_info  = []

        # Iterate over the post pages
        for post_page in range(1, num_post_pages+1):

            try:

                # Get the HTML of the post page
                post_page_soup = requests.get(post_url + 'page/' + str(post_page))
                post_page_soup = BeautifulSoup(post_page_soup.content, 'html.parser')

                # Get the comments of the post page
                comment_boxes = post_page_soup.find_all('div', class_='ipsComment_content ipsType_medium')

            except requests.exceptions.RequestException as e:
                print("Problem connecting and parsing the post page:", str(e))
                continue
            
            for comment_box in comment_boxes:

                # Get the datetime of the comment
                time = comment_box.find('time')['datetime']


                comment_class = 'ipsType_normal ipsType_richText ipsPadding_bottom ipsContained'
                comment_paragraphs = comment_box.find('div', class_=comment_class).find_all('p', recursive=False)


                text = "\n".join([paragraph.text for paragraph in comment_paragraphs])

                # Check the dominant script of the text
                lang = dominant_language(text)

                if(lang == "latin"):
                    
                    comment_info = {
                        "time": time,
                        "text": text
                    }
                    comments_info.append(comment_info)

        return comments_info



if __name__ == "__main__":
    crawler = InsomniaCrawler(data_folder="data_raw")
    crawler.crawl()

    
