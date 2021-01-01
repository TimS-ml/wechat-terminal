import time
import itchat
import _thread
import logging
from os import system
from itchat.content import *
from termcolor import cprint, colored
from pyfiglet import Figlet

# user name of this account
username = str()
# last message FROM (receive msg from) and TO (send msg to)
last_from, last_to = str(), str()
# all WeChat friends and the last 5 WeChat contacts
all_friends, recent_friends = [], []
# thread resource lock
f_lock = _thread.allocate_lock()

# @itchat.msg_register(itchat.content.TEXT)
# def debug_msg(msg):
#     "monitor new message to call this function and show all info of message"
#     print(msg)


def show_help():
    "print help guide in terminal"
    print("""
        Command List
            all                      List all WeChat friends of this account
            ls                       List the last 5 WeChat contacts of this accound
            h                        Show this help guide
            q                        Log out
            s <message>              Send a message to the last TO (you send msg to)
            re <message>             Send a message to the last FROM (you receive msg from)
            s <message> | <name>     Send a message to a friend specified by name
            s <message> || <num>     Send a message to a friend specified by num
            s @fil@<filename>        Send a file (@img@ for image, @vid@ for video)
        """)


def cmd_ctrl():
    # command = input(colored('~> ', 'green', attrs=['bold']))
    # cprint('\n==================================\n', 'magenta')
    command = input('> ')
    command = command.strip()
    command_ = command.casefold()
    # skip space
    if command == "":
        return 0
    elif command_ == "h":
        show_help()
        print()
    elif command_ == "c":
        system('clear')
    elif command_ == "exit" or command_ == "q":
        itchat.logout()
        print()
    elif command_ == "all":
        show_list(all_friends)
        print()
    elif command_ == "ls":
        show_list(recent_friends)
        print()
    elif command.startswith("s") or command.startswith("re"):
        send_format(command)
        print()
    else:
        print("[lol] Invalid Input!")


def launcher_loop():
    "get command from terminal"
    custom_fig = Figlet(font='basic')  # italic / contessa / basic
    print(custom_fig.renderText('Welcome'))
    # loop for refresh info
    while 1:
        # get all friends list
        if not all_friends:
            try:
                get_info()
            except BaseException as e:
                time.sleep(2)
            else:
                print("Loading friends list...")
        else:
            break
    # loop for get command input
    while 1:
        cmd_ctrl()


def get_time():
    "get time and format it"
    return time.strftime('%H:%M:%S')


def get_info():
    "get wechat friends list"
    global username, all_friends
    # get wechat friends set by itchat
    set_friends = itchat.get_friends(update=True)
    # get current user info
    user = set_friends[0]
    username = user['RemarkName'] or user['NickName']
    # traverse set and added name into all_friends list
    for friend in set_friends:
        friend_name = friend['RemarkName'] or friend['NickName']
        all_friends.append(friend_name)
    # sort list
    all_friends.sort()


def update_friends(friend_name):
    "update wechat friends list"
    global all_friends, recent_friends
    # lock data to ensure atomicity
    f_lock.acquire()
    # insert last friend name to front of list
    if friend_name in recent_friends: recent_friends.remove(friend_name)
    recent_friends.insert(0, friend_name)
    if friend_name in all_friends: all_friends.remove(friend_name)
    all_friends.insert(0, friend_name)
    # control recent list length
    if len(recent_friends) > 5:
        recent_friends.pop()
    # release lock after update data
    f_lock.release()


def send_msg(content, friend_name):
    "send message to friends"
    # check message type
    try:
        content.encode('utf-8', 'ignore')
    except Exception as e:
        print("[ERROR] Unsupported message type!")
    else:
        # send message
        try:
            if friend_name == "filehelper":
                itchat.send(content, toUserName='filehelper')
            else:
                friend = itchat.search_friends(friend_name)[0]
                friend.send(content)
        except BaseException as e:
            print("[ERROR] Unable to find this friend!")
        else:
            # output sent message
            time_ = get_time()
            print(f"[{time_}] {username} -> {friend_name} : {content}")
            # update friend list and last TO
            if all_friends: update_friends(friend_name)
            global last_to
            last_to = friend_name


def send_format(command):
    "format send/reply command"
    # send default set to last TO
    if command.startswith("s"):
        command = command.strip("s").strip()
        default = "TO"
    # reply default set to last FROM
    elif command.startswith("re"):
        command = command.strip("re").strip()
        default = "FROM"
    # exit function if there is error
    else:
        print("[ERROR] Unspecified Error!")
        return -1

    # use TO by number if specified
    if command.find("||") >= 0:
        message = command.split(sep="||", maxsplit=1)[0].strip()
        number = command.split(sep="||", maxsplit=1)[1].strip()
        # try to transfer number from string to int
        try:
            number = int(number)
        except Exception as e:
            print("[ERROR] The specified num format is incorrect!")
            return -1
        else:
            if number <= 0 or number > len(all_friends):
                print("[ERROR] The specified num is out of index!")
                return -1
            else:
                friend_name = all_friends[number - 1]
    # use TO by name if specified
    elif command.find("|") >= 0:
        message = command.split(sep="|", maxsplit=1)[0].strip()
        friend_name = command.split(sep="|", maxsplit=1)[1].strip()
    # not specified TO, set as default
    else:
        message = command
        global last_from, last_to
        # "send", set TO as name
        if default == "TO":
            if last_to:
                friend_name = last_to
            else:
                print("[WARN] No Last TO! Please specify reveiver")
                print("e.g. > s <message> | <receiver name>")
                return -1
        # "reply", set FROM as name
        else:
            if last_from:
                friend_name = last_from
            else:
                print("[WARN] No Last FROM! Please specify reveiver")
                print("e.g. > s <message> | <receiver name>")
                return -1
    # call function send message
    send_msg(message, friend_name)


def show_list(friends):
    "show friends list"
    if all_friends:
        for index, friend_name in enumerate(friends):
            index += 1
            print(f"{index}. {friend_name}\t", end="")
    else:
        print("No friend in this list")


@itchat.msg_register(TEXT)
def receive_msg(msg):
    "monitor new message to call this function"
    # get message content
    content = msg['Text']
    # get message time
    time_ = get_time()
    # get message sender
    if "RemarkName" in msg['User']:
        friend_name = msg['User']['RemarkName'] or msg['User']['NickName']
    else:
        friend_name = msg['User']['UserName']
    # show received message
    if msg['FromUserName'] == msg['User']['UserName']:
        print(f"\n[{time_}] {friend_name} -> {username} : {content}\n> ",
              end='')
    # show sent message
    else:
        print(f"\n[{time_}] {username} -> {friend_name} : {content}\n> ",
              end='')
    # update friend list and last FROM
    if all_friends: update_friends(friend_name)
    global last_from
    last_from = friend_name


@itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO])
def download_files(msg):
    # download it
    msg.download(msg.fileName)
    # get message time
    time_ = get_time()
    # get message sender
    if "RemarkName" in msg['User']:
        friend_name = msg['User']['RemarkName'] or msg['User']['NickName']
    else:
        friend_name = msg['User']['UserName']
    # show received message
    if msg['FromUserName'] == msg['User']['UserName']:
        print(
            f"\n[{time_}] {friend_name} -> {username} : {msg.fileName} received\n> ",
            end='')
    # show sent message
    else:
        print(
            f"\n[{time_}] {username} -> {friend_name} : {msg.fileName} send\n> ",
            end='')
    # update friend list and last FROM
    if all_friends: update_friends(friend_name)
    global last_from
    last_from = friend_name


def main():
    "main function"
    # disable itchat debug log
    logging.disable(logging.DEBUG)
    # create a thread for monitor command
    _thread.start_new_thread(launcher_loop, ())
    # itchat login
    itchat.auto_login(hotReload=True)
    # itchat run
    itchat.run(True)


if __name__ == '__main__':
    main()
