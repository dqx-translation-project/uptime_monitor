import json
import requests
import socket
from datetime import datetime
from servers import SERVERS


server_status = {
    "launcher": {
        "status": "",
        "message": ""
    },
    "login_router": {
        "status": ""
    },
    "game_servers": {},
    "last_updated": ""
}


def check_server_connection(server: str) -> bool:
    ip, port = server.split(":")

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(3)
    result = s.connect_ex((ip, int(port)))
    if result == 0:
        return True
    return False


def check_launcher_connection():
    headers = {
        'User-Agent': 'Server State Check',
        'Cache-Control': 'no-cache',
        'Host': 'game.dqx.jp'
    }
    response = requests.get(SERVERS.get('launcher'), headers=headers)
    if response.status_code == 200:
        status = json.loads(response.text, strict=False)
        if status.get('status') == '0':
            server_status['launcher'].update(status='up')
        else:
            server_status['launcher'].update(status='down')
            if message := status.get('text'):
                server_status['launcher'].update(message=message)
    else:
        server_status['launcher'].update(status='down')


def run_connection_tests():
    check_launcher_connection()

    login_router_check = check_server_connection(server=SERVERS.get('login_router'))
    if login_router_check:
        server_status['login_router']['status'] = 'up'
    else:
        server_status['login_router']['status'] = 'down'

    for server in SERVERS.get('game_servers'):
        check = check_server_connection(server=server)
        if check:
            server_status['game_servers'][server.split(":")[0]] = 'up'
        else:
            server_status['game_servers'][server.split(":")[0]] = 'down'

    server_status['last_updated'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')


def main():
    run_connection_tests()
    data = json.dumps(server_status, indent=2, ensure_ascii=False)
    with open("./status.json", "w+") as f:
        f.write(data)


if __name__ == "__main__":
    main()
