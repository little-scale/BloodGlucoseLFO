import requests
from pythonosc import udp_client
from pythonosc.osc_message_builder import OscMessageBuilder

osc_ip = "127.0.0.1"
osc_port = 1337
osc_address = "/libre/data"

client = udp_client.SimpleUDPClient(osc_ip, osc_port)

libre_login = "your email"
libre_password = "your password"

api_endpoint = 'https://api-au.libreview.io'
# eu2 is the region, current options available are:
# "us", "eu", "de", "fr", "jp", "ap", "au", "ae", "eu2", "ca", "worldwide"

headers= {
    'accept-encoding': 'gzip, deflate, br',
    'cache-control': 'no-cache',
    'connection': 'Keep-Alive',
    'content-type': 'application/json',
    'product': 'llu.ios',
    'version': '4.9.0'
}

loginData = {"email": libre_login, "password": libre_password}
r = requests.post(url = api_endpoint + "/llu/auth/login", headers=headers, json=loginData)
data = r.json()

JWT_token = data['data']['authTicket']['token']
extra_header_info = {'authorization': 'Bearer ' + JWT_token}
headers.update(extra_header_info) # or save the token to the user's db

r = requests.get(url = api_endpoint + "/llu/connections", headers=headers)
data = r.json()
patient_id = data['data'][0]['patientId']

r = requests.get(url = api_endpoint + "/llu/connections/" + patient_id + "/graph", headers=headers)
data = r.json()["data"]

historical = data["graphData"] # data for the past 12 hours (excluding latest reading)

builder = OscMessageBuilder(address = osc_address)

if historical is not None:
    entries = historical
latest = data["connection"]["glucoseMeasurement"] # latest reading
if latest is not None:
    entries.append(latest)
for item in entries:
    builder.add_arg(item['Value'])
msg = builder.build()
client.send(msg)
print(entries)











