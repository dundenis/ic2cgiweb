#!/usr/bin/python3

import json
import cgi
from datetime import datetime
import requests


class hosts():
    def __init__(self, hostName):
        self.connection_error = ""
        queryUrl = 'https://localhost:5665/v1/objects/hosts?host='+hostName
        self.query_args = {'url': queryUrl,
                           'headers': {'Accept': 'application/json', 'X-HTTP-Method-Override': 'GET'},
                           #'data': {'attrs': ['name',
                        #                  'address',
                        #                      'state',
                        #                      'last_check',
                        ###                      'last_state_change'
                            #                  ]
                            #        }
                           }
        #self.list = []
        self.response = ""
        self.get_hosts_from_api()  # request to icinga
        #self.filtered_rows = 0
        #if self.connection_error == "":
        #    self.gen_list()  # add list from icinga's response
        #    self.get_total_rows()


    def get_hosts_from_api(self):  # do request to icinga via api
        try:
            req = requests.post(url=self.query_args['url'],
                                headers=self.query_args['headers'],
                                auth=('root', '123456'),
                                #data=json.dumps(self.query_args['data']),
                                verify="/var/www/server/cgi-bin/ca.crt"
                                )
        except requests.exceptions.RequestException as error_data:
            self.connection_error = error_data
            #sys.exit(1)  # if error - exit script
        else:
            self.response = req.json()['results'][0] # return dict in json format

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
        r = re.compile(str(search_value))
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
        self.hostName = str(cgi.FieldStorage()['hostName'].value)
        #self.data = json.loads(data)
        #self.parse()

    #def parse(self):
    #    self.hostName = str(self.data['hostName'])

def main():
    req = query()
    resp = hosts(req.hostName)
 #   if resp.connection_error != "":
 #       errdata = "\nERROR connection to icinga2 api:\n"+str(resp.connection_error)
 #       body = json.dumps({"draw":req.draw,"error": errdata})
 #       print("Status: 200 OK")
 #       print("Content-Type: application/json")
 #       print("Length:", len(body))
 #       print("")
 #       print(body)
 #   else:

    body = """
      <div class="ui celled list">
  <div class="item">
    
    <div class="content">
      <div class="header">Snickerdoodle</div>
      An excellent companion
    </div>
  </div>
  <div class="item">
    
    <div class="content">
      <div class="header">Poodle</div>
      A poodle, its pretty basic
    </div>
  </div>
  <div class="item">
    
    <div class="content">
      <div class="header">Paulo</div>
      He's also a dog
    </div>
  </div>
</div>"""
    print("Status: 200 OK")
    #print("Content-Type: application/json")
    print("Content-type: text/html")
    print("Length:", len(body))
    print("")
    print(body)

if __name__ == '__main__':
    main()
