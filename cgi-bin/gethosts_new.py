#!/usr/bin/python3

import json
#import sys
import cgi
from datetime import datetime
import requests
import re
from operator import itemgetter
from multiprocessing import Pool

#class host:
#    def __init__(self, address, name, last_check, state):
#        self.address = address
#        self.name = name
#        self.last_check = last_check
#        self.state = state
#
#    def __repr__(self):
#        return repr((self.address, self.name, self.last_check, self.state))


class hosts():
    def __init__(self):
        self.connection_error = ""
        self.query_args = {'url': 'https://localhost:5665/v1/objects/hosts',
                           'headers': {'Accept': 'application/json', 'X-HTTP-Method-Override': 'GET'},
                           'data': {'attrs': ['name',
                                              'address',
                                              'state',
                                              'last_check',
                                              'last_state_up',
                                              'last_state_down',
                                              'last_state_change'
                                              ]
                                    }
                           }
        self.list = []
        self.response = ""
        self.get_hosts_from_api()  # request to icinga
        if self.connection_error == "":
            self.gen_list()  # add list from icinga's response
            self.get_total_rows()
            self.filtered_rows = self.total_rows


    def get_hosts_from_api(self):  # do request to icinga via api
        try:
            req = requests.post(url=self.query_args['url'],
                                headers=self.query_args['headers'],
                                auth=('root', '123456'),
                                data=json.dumps(self.query_args['data']),
                                verify="/var/www/server/cgi-bin/ca.crt"
                                )
        except requests.exceptions.RequestException as error_data:
            self.connection_error = error_data
            #sys.exit(1)  # if error - exit script
        else:
            self.response = req.json()['results']  # return dict in json format

    def get_attrs(self, item):
        hostname = item['name']
        host_state = item['attrs']['state']
        host_address = item['attrs']['address']
        host_time = {'last_check': item['attrs']['last_check'],
                     'last_state_up': item['attrs']['last_state_up'],
                     'last_state_down': item['attrs']['last_state_down'],
                     'last_state_change': item['attrs']['last_state_change']
                     }
        if host_state == 0:
            host_state = "UP"
        else:
            host_state = "DOWN"

        for time in host_time:
            host_time[time] = datetime.fromtimestamp(host_time[time]).strftime('%Y-%m-%d %H:%M:%S')

        return {'hostName': str(hostname),
                'ipAddress': str(host_address),
                'lastCheck': str(host_time['last_check']),
                'lastStateChange': str(host_time['last_state_change']),
                'hostState': str(host_state)
                }

    def gen_list(self):
        #with Pool(1) as p:
        #    self.list = list(p.map(self.get_attrs,self.response))
        self.list = list(map(self.get_attrs,self.response))

    def sorting(self, col, desc=True):
        table = (None,'hostName', 'ipAddress', 'lastCheck','lastStateChange','hostState')
        self.list = sorted(self.list, key=itemgetter(table[col]), reverse=desc)

    def filter(self, search_value):
        #self.list=[item for item in self.list if search in item]
        templist = []
        s = str(search_value)
        r = re.compile(s)
        for row in self.list:
            for key, value in row.items():
                if r.search(value):
                    templist.append(row)
                    break
        self.filtered_rows = len(templist)
        self.list = templist

    def getResultJSON(self, draw=1, start=None, length=None):
        self.result = {"draw": draw,
                       "recordsTotal": self.total_rows,
                       "recordsFiltered": self.filtered_rows}
        end = start + length
        data = []
        for host in self.list[start:end]:
            data.append(host)
        self.result.update({"data": data})

    def get_total_rows(self):
        self.total_rows = len(self.list)

class query:
    def __init__(self):
        self.data = json.loads(cgi.FieldStorage()['json'].value)
        # self.data = json.loads(data)
        self.parse()

    def parse(self):
        self.draw = self.data['draw']
        self.start = self.data['start']
        self.length = self.data['length']
        self.search = self.data['search']['value']
        self.order_col = self.data['order'][0]['column']
        rev = self.data['order'][0]['dir']
        if rev == "desc":
            self.order_reverse = True
        else:
            self.order_reverse = False

def main():
    req = query()
    resp = hosts()
 #   if resp.connection_error != "":
 #       errdata = "\nERROR connection to icinga2 api:\n"+str(resp.connection_error)
 #       body = json.dumps({"draw":req.draw,"error": errdata})
 #       print("Status: 200 OK")
 #       print("Content-Type: application/json")
 #       print("Length:", len(body))
 #       print("")
 #       print(body)
 #   else:
    if req.search !='':
        resp.filter(req.search)

    resp.sorting(req.order_col, desc=req.order_reverse)
    resp.getResultJSON(req.draw, req.start, req.length)
    body = json.dumps(resp.result)
    print("Status: 200 OK")
    print("Content-Type: application/json")
    print("Length:", len(body))
    print("")
    print(body)

if __name__ == '__main__':
    main()













# def get_range(page=1, rows=10):
#    start = (page - 1) * rows
#    end = start + rows
#    range = {'start':start,'end':end}
#    print (range)



# def in_html(self, data, **args):
# rows = get_page_row(args['npage'], args['rows'], data)
#    rows = len(self.list)
#    self.html_tab = """<table>\n"""
#    for row in rows:
#        self.html_tab += "<tr>\n"
#        for col in row:
#            tab += "<td>" + str(col) + "</td>\n"
#            tab += "</tr>\n"
#    self.html_tab += "</table>\n"

# def get_page_row(npage, rows_per_page, data):  # get rows range for pagination
#     start = (npage - 1) * rows_per_page
#     end = start + rows_per_page
#     newrange = [row for row in data]
#     return newrange[start:end]

# request_url = "https://localhost:5665/v1/objects/hosts"
# headers = {'Accept': 'application/json',
#           'X-HTTP-Method-Override': 'GET'
#           }
# data = {'attrs': ['name', 'address', 'state', 'last_check']
#        }
# response = get_hosts(request_url, headers, data)
# args = {'npage': 2, 'rows': 20}
# print("Content-type: text/html")
# print()
# print_table(gen_hosts_list(), **args)
