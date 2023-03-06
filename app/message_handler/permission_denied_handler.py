# permission_denied_handler.py
from utils.message_sender import Msg_struct, send_message

def permission_denied(gid=None, qid=None):
    message = '权限不足'
    if gid:
        message = f'[CQ:at,qq={qid}]' + message
    msg_struct = Msg_struct(gid=gid, qid=qid, msg=message)
    send_message(msg_struct)
