# message_handler.py
import re
import requests
from app.message_handler.bot_commands import BotCommands
from app.message_handler.command_error_handler import command_error_handler
from app.message_handler.permission_denied_handler import permission_denied
from app.message_handler.service_registry import serviceRegistry
from queue import Queue
import time

message_queue = Queue()

def message_forwarding():
    while True:
        message = message_queue.get(block=True)
        url = message['url']
        json = message['json']
        response = requests.post(url, json=json)
        result_dict = response.json()
        permission = result_dict['permission']
        gid = json['gid']
        qid = json['qid']
        if not permission:
            permission_denied(gid=gid, qid=qid)
        print(f"Message forwarded to {url}")
        time.sleep(0.1)

def message_handler(message: str, gid=None, qid=None):
    def check_command(message, command_list):
        pattern = r'(#\w+)\s*(.*)'
        match = re.match(pattern, message.strip())
        if match:
            command = match.group(1)
            if command in command_list:
                param_list = match.group(2).strip().split()
                return command, param_list
            else:
                return 'error', 'invalid command'
        else:
            return None, None
    commands = list(BotCommands.get_commands())
    command, param_list = check_command(message, commands)
    if command:
        if 'error' == command:
            command_error_handler(gid, qid)
        else:
            service_name = BotCommands.get_service_name(command)
            service_info = serviceRegistry.get_service(service_name)
            if service_info is not None:
                service_ip = service_info['ip']
                service_port = service_info['port']
                endpoint = service_info['endpoints']['receive_command']
                url = f"http://{service_ip}:{service_port}/{endpoint}"
                message = {
                    'url':url,
                    'json': {'command': command, 'args': param_list, 'gid': gid, 'qid': qid}
                }
                message_queue.put(message)
