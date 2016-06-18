from __future__ import print_function
from six import iteritems
import json
from time import strftime, sleep
root = "E:\\Projects\swarm-relayr\\"
template_filename = root + "template.html"
output_filename = root + "index.html"
zones_filename = root + "zones.json"
data_list = {}
zones = {}

def handle_data(data):
    print("handle_data", data)
    global template_filename
    global output_filename
    global zones
    global data_list

    #if data["node_id"] in data_list:
    data_list[data["node_id"]] = data["distance"]

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
        current = zones[id]
        criteria = current["criteria"]
        detected = True
        
        for item in criteria:
            detected = detected and is_match(data, item)
            if not detected:
                print("Nope!")
                break
                
        if not detected:
            print("Trying next zone...")
            continue
        else:
            print("Zone detected: " + id)
            return id
            
    if not detected:
        print("I am in No Man's Land!")
        return None
            
def is_match(data, criterium):
    node_id = criterium["node_id"]
    type = criterium["type"]
    value = criterium["value"]
    
    result = True
    print(json.dumps(data))
    print(json.dumps(criterium))
    for item_node_id, distance in iteritems(data):
        if node_id == item_node_id:
            if type == "lt":
                result = result and (distance < value)
            elif type == "gt":
                result = result and (distance > value)
            elif type == "lteq":
                result = result and (distance <= value) 
            elif type == "gteq":
                result = result and (distance >= value)
            else:
                print("Unknown operation: " + type)
        else:
            result = False
    if result:
        print("JA!")
    return result
    
    
def load_zones():
    global zones
    global zones_filename
    
    with open(zones_filename) as f:
        zones = json.load(f)
        

def load_fake_data():
    return {"1": 140.5, "2": 350.7, "3": 560.1}
    
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
    