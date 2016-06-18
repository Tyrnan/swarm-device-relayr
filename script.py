from __future__ import print_function
from six import iteritems
import json
from time import strftime, sleep

root = "E:\\Projects\\swarm-relayr\\"
template_filename = "template.html"
output_filename = root + "index.html"
zones_filename = root + "zones.json"

zones = {}
data_list = {}
fake_data = []
i = -1


def handle_data(data):
    global template_filename
    global output_filename
    global zones
    global data_list
    
    data_list[data["node_id"]] = data["distance"]
    print("data_list:")
    print(json.dumps(data_list))
    
    template = load_html_template(template_filename)
    zone_id = detect_zone(data_list, zones)
    if zone_id is not None:
        zone = zones[zone_id]
        output_data = {"message": zone["message"], "color": zone["color"], "zone": zone_id}
    else:
        output_data = {"message": "Location unknown!", "color": "#880000", "zone": ""}
    
    write_html(template, output_data, output_filename)
    
    
def detect_zone(data, zones):
    for id in zones:
        print("Am I in zone " + id + "?")
        
        print(json.dumps(data))
        
        current = zones[id]
        criteria = current["criteria"]
        detected = True
        
        for item in criteria:
            print(json.dumps(criteria))
            detected = detected and is_match(data, item)
            if not detected:
                print("Criterium does not match data!")
                break
                
        if not detected:
            print("Trying next zone...")
            continue
        else:
            print("====================================")
            print("Zone detected: " + id)
            print("====================================")
            return id
            
    if not detected:
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("I am in No Man's Land!")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        return None
            
def is_match(data, criterium):
    node_id = criterium["node_id"]
    type = criterium["type"]
    value = criterium["value"]
    
    result = True
    print(str(node_id) + " in data?")
    if node_id in data:
        distance = data[node_id]
        print("Yes")
        if type == "lt":
            print(str(distance) + " < " + str(value) + "?")
            print(distance < value)
            result = result and (distance < value)
            print(result)
            if result:
                print("Yes")
            else:
                print("No")
        elif type == "gt":
            print(str(distance) + " >" + str(value) + "?")
            result = result and (distance > value)
            print(distance > value)
            print(result)
            if result:
                print("Yes")
            else:
                print("No")
        elif type == "lteq":
            print(str(distance) + " <= " + str(value) + "?")
            result = result and (distance <= value) 
            if result:
                print("Yes")
            else:
                print("No")
        elif type == "gteq":
            print(str(distance) + " >= " + str(value) + "?")
            result = result and (distance >= value)
            if result:
                print("Yes")
            else:
                print("No")
        else:
            print("Unknown operation: " + type)
            
        return result
    else:
        return False
    
    
def load_zones():
    global zones
    global zones_filename
    
    with open(zones_filename) as f:
        zones = json.load(f)
        

def load_fake_data():
    global fake_data
    global i
    
    if i < 0:
        with open("C:\\Users\\aw16246\\Documents\\Projekte\\mindbox hackday 2016\\log.txt") as f:
            fake_data = f.readlines()
        i = 0
        
    result = json.loads(fake_data[i])
    print(json.dumps(result))
    i = i+1
    return result
    #return {645456: 140.5, 678678: 350.7, 67678678: 560.1}
    
def load_html_template(filename):
    with open(filename) as f:
        template = f.read()
    
    return template
    
def write_html(template, data, filename):
    for name in data:
        template = template.replace("{" + name + "}", data[name])
    
    with open(filename, "w") as f:
        f.write(template)
    
if __name__ == "__main__":
    load_zones()
    while True:
        data = load_fake_data()
        handle_data(data)
        print(strftime("%Y-%m-%d %H:%M:%S"))
        sleep(1)
    