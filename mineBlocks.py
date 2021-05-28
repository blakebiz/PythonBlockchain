import requests, json

def mine_block():
    return requests.get("http://127.0.0.1:5000/mine_block").text.replace("'", '"')


def get_chain():
    return requests.get("http://127.0.0.1:5000/get_chain").text.replace("'", '"')


def is_valid():
    return requests.get("http://127.0.0.1:5000/is_valid").text.replace("'", '"')


def check_avg_mine_time():
    return requests.get("http://127.0.0.1:5000/avg_mine_time").text.replace("'", '"')


for _ in range(100):
    print(mine_block())
print(json.dumps(json.loads(get_chain()), indent=4))
print(is_valid())
print(json.dumps(json.loads(check_avg_mine_time()), indent=4))
