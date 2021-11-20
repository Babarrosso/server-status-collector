from typing import Text
from urllib import request as urlrequest
from bs4 import BeautifulSoup
import argparse
import sched, time

parser = argparse.ArgumentParser(description='Collecting Paths included in Apache Server Status Page.', add_help=False)
required = parser.add_argument_group('Required Arguments')
optional = parser.add_argument_group('Optional Arguments')

required.add_argument("-u", help="URL which will be requested", required=True)

optional.add_argument("-o", "--output",default="output.txt",help="File for storing the collected Paths")
optional.add_argument("-t", "--time", type=int, default=5, help="Time interval between Requests in ms")
optional.add_argument("-p", "--proxy", help="Proxy to use")
optional.add_argument("-h", "--help", action="help", default=argparse.SUPPRESS, help="Show this help message and exit")
args = parser.parse_args()

url = args.u
outputfile = args.output
seconds = args.time
proxy_host = args.proxy

req = urlrequest.Request(url)

if proxy_host is not None:
    req.set_proxy(proxy_host, 'http')

response = urlrequest.urlopen(req)
html = response.read().decode('utf8')

paths = list()

s = sched.scheduler(time.time, time.sleep)

def check_duplicates(new_path, paths):
    if new_path in paths:
        return True
    else:
        return False

def extract_path(html):
    soup = BeautifulSoup(html, 'html.parser')
    for row in soup.find_all('table')[0].find_all('tr')[1:]:
        
        last_column = row.find_all('td')[-1].text
        
        if last_column != "" or last_column != "/server-status" or last_column != "/":
            request = str(last_column).split()
            
            if len(request) == 3 and request[1] != '*':
                if check_duplicates(request[1], paths) == False:
                    paths.append(request[1]) 
    paths.sort()
    print(paths)
    save_to_file(paths,outputfile)
    s.enter(seconds,1,extract_path,(html,))

def save_to_file(paths, outputfile):
    with open (outputfile, 'a') as f:   
        for path in paths:
            f.write(path + "\n")

def main():
    
    s.enter(seconds,1,extract_path,(html,))
    s.run()

if __name__ == "__main__":
    main()