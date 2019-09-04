import requests
import common_functions as common
from datetime import datetime
from bs4 import BeautifulSoup as bs


def get_request(url, proxy=None):
    user_agent = common.get_rand_user_agent_from_file("C:\\Users\\ulens\\PycharmProjects\\football_parser\\assets\\useragents.txt")
    # Proxies = {'https': 'https://3.93.151.128:8080'}
    # Proxies = {'https': 'https://89.29.100.212:3128'}
    # Proxies = {'https': 'https://54.37.136.149:3128'}
    # Proxies = {'https': 'https://195.230.131.210:3128'}
    Proxies = {'https': 'https://40.68.149.233:8080'}

    # Proxies = {'https': f'https://{proxy}'} if proxy else {}
    try:
        request = requests.get(url, headers={'User-Agent': user_agent}, proxies=Proxies)
        # for k,v in request.headers.items():
        #     print(k, ": ", v)
        if request.status_code is not 200:
            raise Exception(f"Error get request: {str(request.status_code)}")
        return request

    except requests.exceptions.HTTPError as e:
        raise Exception(e)
    except requests.exceptions.RequestException as e:
        raise Exception(e)
    except Exception as Err:
        raise Exception(Err)


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