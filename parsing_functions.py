import requests
import common_functions as common
from datetime import datetime
from bs4 import BeautifulSoup as bs

def get_contents(url, elem, selector):
    request = get_request(url)
    soup = bs(request.text, 'html.parser')
    content = soup.find_all(elem, selector)
    return content


def get_content(url, elem, selector):
    request = get_request(url)
    if request is not None:
        soup = bs(request.text, 'html.parser')
        content = soup.find(elem, selector)
        return content


def log_not_parsing(url, message):
    try:
        current_datetime = datetime.today().strftime("%d_%m_%y-%H_%M_%S")
        log_file = open("logs\\logfile_"+current_datetime+".txt", 'w')

        log_file.write(message)
        log_file.write(datetime.today().strftime("%d-%m-%y %H:%M:%S")+' Not parsing url: '+url)
        log_file.write("/n")
        log_file.close()
    except Exception as e:
        print('Log writing error: '+str(e))
        raise SystemExit()