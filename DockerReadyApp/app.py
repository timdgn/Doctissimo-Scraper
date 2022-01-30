from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from time import sleep, time
import pandas as pd
import boto3
from io import StringIO
#import json

def lambda_handler(event=None, context=None):
    """
    Handler function definition for AWS Lambda.
    """
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = "/opt/chrome/stable/chrome"
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-tools")
    chrome_options.add_argument("--no-zygote")
    chrome_options.add_argument("--single-process")
    chrome_options.add_argument("window-size=2560x1440")
    chrome_options.add_argument("--user-data-dir=/tmp/chrome-user-data")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--user-data-dir=/tmp/chrome-user-data")
    driver = webdriver.Chrome("/opt/chromedriver/stable/chromedriver", options=chrome_options)





    ############################################################################
    #                                                                          #
    #                                                                          #
    #                          Functions Declarations                          #
    #                                                                          #
    #                                                                          #
    ############################################################################

    def create_urls(url, pages):
        """
        Creates a list of all the URLs of a forum.

        Args:
            url (str): URL of a forum (like "https://forum.doctissimo.fr/sante/diabete/liste_sujet-1.htm").
            pages (int): Number of pages of a forum you want to scrap.

        Returns:
            list: List of URLs of a forum
        """
        url_base = url.split("1.htm",1)[0]
        return [url_base + str(i) + '.htm' for i in range(1,pages+1)]

    def topics_extractor_class(forum_urls):
        """
        Takes a list of URLs of a forum,
        and returns some lists of all topics URLs and many other infos.

        Args:
            forum_urls (list): List of URLs of a forum. This list is created by the function create_urls.

        Returns:
            lists: Returns six lists (topic urls, topic numbers, topic names,
                topic authors, topic replies number and topic read numbers)
        """
        list_topics_urls = []
        list_topics_numbers = []
        list_topics_names = []
        list_topics_authors = []
        list_nb_replies = []
        list_nb_reads = []

        for url in forum_urls:
            driver.get(url)
            lines = driver.find_elements(By.CSS_SELECTOR, '.sujet.ligne_booleen')
            for line in lines:
                
                central_part = line.find_elements(By.CSS_SELECTOR, '.sujetCase3')[0]
                
                topic_url = central_part.find_elements(By.TAG_NAME, 'a')[0].get_attribute('href')
                list_topics_urls.append(topic_url)

                topic_name = central_part.find_elements(By.TAG_NAME, 'a')[0].text
                list_topics_names.append(topic_name)

                topic_author = (line.find_elements(By.CSS_SELECTOR,
                    '.sujetCase6.cBackCouleurTab2') + line.find_elements(By.CSS_SELECTOR,
                    '.sujetCase6.cBackCouleurTab4'))[0].text
                list_topics_authors.append(topic_author)

                nb_replies = line.find_elements(By.CSS_SELECTOR, '.sujetCase7')[0].text
                list_nb_replies.append(nb_replies)

                nb_reads = line.find_elements(By.CSS_SELECTOR, '.sujetCase8')[0].text
                list_nb_reads.append(nb_reads)

        for element in list_topics_urls:
            topic_number = element.split("_",2)[1]
            list_topics_numbers.append(topic_number)

        return list_topics_urls[2:], list_topics_numbers[2:], list_topics_names[2:], list_topics_authors[2:], list_nb_replies[2:], list_nb_reads[2:]

    def vp_button_click():
        """
        This function clicks on the "Voir plus" button in a topic.
        """
        button_class = '.MuiButtonBase-root.MuiButton-root.MuiButton-text.SHRD__sc-dvq2vt-3'
        button = driver.find_element(By.CSS_SELECTOR, button_class)
        button.click()

    def find_max_page():
        """
        This function clicks on the "Voir plus" button in a topic.

        Returns:
            int: The number of pages of the topic.
        """
        page_numbers = []
        number_class = '.SHRD__sc-1ymbfjb-0.jgGWVT'
        numbers_class = driver.find_elements(By.CSS_SELECTOR, number_class)
        page_numbers += [element.text for element in numbers_class]

        # Return the highest number of the page_numbers list
        # If there's only 1 page, page_numbers equals 0
        return 1 if not page_numbers else int(page_numbers[-1])

    def nb_pages():
        """
        This function returns the total number of pages of a topic after clicking on "Voir plus" (if there is one).
        It uses the vp_button_click and the find_max_page functions.

        Returns:
            int: The number of pages of the topic.
        """
        try:
            vp_button_click()
        except (NoSuchElementException):
            print("Not a lot of pages in this topic ! 😍")
        else:
            print("There is quite a few pages here ! 😵‍💫")
        return find_max_page()





    ############################################################################
    #                                                                          #
    #                                                                          #
    #                             Initialisation                               #
    #                                                                          #
    #                                                                          #
    ############################################################################

    # Fetch the URL of the subject list to trigger the cookie requirements.
    url = 'https://forum.doctissimo.fr/sante/diabete/liste_sujet-1.htm'
    driver.get(url)

    # Wait and accept the cookies if it's asked
    print("\nWait for the cookies ... 🍪")
    sleep(3)
    try:
        button = driver.find_element(By.ID, 'didomi-notice-agree-button')
        button.click()
        print("Cookie request accepted ! 😋")
    except (RuntimeError, TypeError, NameError, NoSuchElementException):
        print("No cookies")





    ############################################################################
    #                                                                          #
    #                                                                          #
    #                   Fetching the URLs of all the topics                    #
    #                                                                          #
    #                                                                          #
    ############################################################################

    forum_url = "https://forum.doctissimo.fr/sante/diabete/liste_sujet-1.htm"
    page_max_forum = 1
    print("\nOkey, let's first start getting the topics URLs ! \nIt will take some time so don't worry 😉")
    t1 = time()

    # Creates a list of all the URLs of the forum.
    forum_urls = create_urls(forum_url, page_max_forum)

    # Defines the variables and launch the scrapping of the topis URLs
    list_topics_urls, list_topics_numbers, list_topics_names, list_topics_authors, list_nb_replies, list_nb_reads = topics_extractor_class(forum_urls)
    t2 = time()

    # Notice the time spent on this step
    time_spent_min = (t2-t1)/60
    avg_time_sec = (t2-t1)/len(forum_urls)
    print("\nThe " + str(len(forum_urls)) + " pages are done !")
    print("The scraping took " + str("%.2f"%time_spent_min) + " mins (" + str("%.2f"%(time_spent_min/60)) + " hours)")
    print("Thats an average of " + str("%.2f"%avg_time_sec) + " s/page")


    # Cleans the spaces from list_nb_replies and list_nb_reads
    # to make them integers instead of strings.
    list_nb_replies = [element.replace(" ", "") for element in list_nb_replies]
    list_nb_reads = [element.replace(" ", "") for element in list_nb_reads]

    # Creates a dataframe and export to csv if wanted.
    df_list_topics_urls = pd.DataFrame(
        {'Topics URL': list_topics_urls,
        'Topic Number': list_topics_numbers,
        'Topic Name': list_topics_names,
        'Topic Author': list_topics_authors,
        'Topic Replies Nb': list_nb_replies,
        'Topic Reads Nb': list_nb_reads})
    # export_path = '/Users/tim/OneDrive - Data ScienceTech Institute/Konvoo_project/scrapped_data_without_nb_pages.csv'
    # df_list_topics_urls.to_csv(export_path, encoding='utf-8-sig', sep = ';', index=False)





    ############################################################################
    #                                                                          #
    #                                                                          #
    #              Fetching the number of pages of each topic                  #
    #                                                                          #
    #                                                                          #
    ############################################################################

    # Connect to the list_topics_urls
    # and get the numbers of pages.
    list_nb_pages = []
    print("\nDone ✅ \nTime for the scraping of all these URLs now ! ⛏")
    t1 = time()
    for url in list_topics_urls:
            driver.get(url)
            print("\nTopic No. " + str(list_topics_urls.index(url)+1) + "/" + str(len(list_topics_urls)) + " ...")
            list_nb_pages.append(nb_pages())
    t2 = time()

    # Notice the time spent on this step
    time_spent_min = (t2-t1)/60
    avg_time_sec = (t2-t1)/len(list_topics_urls)
    print("\nThe " + str(len(list_topics_urls)) + " pages are done !")
    print("The scraping took " + str("%.2f"%time_spent_min) + " mins (" + str("%.2f"%(time_spent_min/60)) + " hours)")
    print("Thats an average of " + str("%.2f"%avg_time_sec) + " s/page")

    # Close the driver
    print("\nClosing the webdriver.")
    driver.quit()

    # Add the numbers of pages to the df_list_topics_urls dataframe previously created
    # and export to csv.
    df_list_topics_urls['Nb of pages'] = list_nb_pages
    # export_path = '/Users/tim/OneDrive - Data ScienceTech Institute/Konvoo_project/scrapped_data_nb_pages.csv'
    # df_list_topics_urls.to_csv(export_path, encoding='utf-8-sig', sep = ';', index=False)





    ############################################################################
    #                                                                          #
    #                                                                          #
    #             Creating the list of all the URLs for each topic             #
    #                                                                          #
    #                                                                          #
    ############################################################################

    # Create a list 'all_topics_urls' that will contain every list of URLs for each topic.
    # The architecture is the following :
    # all_topics_urls[ [list_urls_topic1], [list_urls_topic2], [list_urls_topic3], ...]
    all_topics_urls = []
    for i in range(len(list_topics_urls)):
        url = list_topics_urls[i]
        pages = list_nb_pages[i]
        all_topics_urls.append(create_urls(url, pages))

    # Add all the URLs to the df_list_topics_urls dataframe previously created.
    df_list_topics_urls['All URLs'] = all_topics_urls
    print("\n\n\nScraping done, good job ! 💪\n\n\n")


    # Create and export a not-locally-stored .csv file to bucket :
    csv_buffer = StringIO()
    df_list_topics_urls.to_csv(csv_buffer)
    Body=csv_buffer.getvalue()

    bucket_name = 'konvoo'
    uploaded_file_name = 'URLs_export.csv'

    s3_resource = boto3.resource('s3')
    s3_resource.Object(bucket_name, uploaded_file_name).put(Body=Body)
    print("\n\n\nExport to s3 Bucket done ✅\n\n\n")


    return 'Hello from Lambda, mission complete !'