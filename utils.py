import time
import pickle
from os import path
# from tabulate import tabulate
from texttable import Texttable


def save_var(username, last, friends):
    with open('./stuff.pkl', 'wb') as f:
        pickle.dump(username, f)
        pickle.dump(last, f)
        pickle.dump(friends, f)
    print('Variable saved\n')


def load_var():
    if path.exists('./stuff.pkl'):
        with open('./stuff.pkl', 'rb') as f:
            username = pickle.load(f)
            [last_from, last_to] = pickle.load(f)
            [all_friends, recent_friends] = pickle.load(f)
        print('Variable loaded')
    else:
        username = str()
        last_from, last_to = str(), str()
        all_friends, recent_friends = [], []
        print('Init variable')
    return username, last_from, last_to, all_friends, recent_friends


def get_time():
    "get time and format it"
    return time.strftime('%H:%M:%S')


def show_list(friends):
    "show friends list"
    L = len(friends)
    index = [i for i in range(1, L + 1)]
    if L < 20:
        # temp = list(zip(index, friends))
        temp = list(
            zip(
                index[:int(L / 2)],
                friends[:int(L / 2)],
                index[int(L / 2):int(L)],
                friends[int(L / 2):int(L)],
            ))
    else:
        temp = list(
            zip(
                index[:int(L / 4)],
                friends[:int(L / 4)],
                index[int(L / 4):int(L / 2)],
                friends[int(L / 4):int(L / 2)],
                index[int(L / 2):int(L * 3 / 4)],
                friends[int(L / 2):int(L * 3 / 4)],
                index[int(L * 3 / 4):int(L)],
                friends[int(L * 3 / 4):int(L)],
            ))
    # print(tabulate(temp))
    table = Texttable()
    table.add_rows(temp, header=False)
    print(table.draw())


def find_friend(command, all_friends):
    "filter friends by kws"
    kws = command.strip("f").strip()
    temp = []
    for key, friend_name in enumerate(all_friends):
        if kws in friend_name:
            temp.append([key+ 1, friend_name])
    # print(tabulate(temp))
    table = Texttable()
    table.add_rows(temp, header=False)
    print(table.draw())


def send_format(command, last_from, last_to, all_friends):
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
    if command.find("-n") >= 0:
        message = command.split(sep="-n", maxsplit=1)[0].strip()
        number = command.split(sep="-n", maxsplit=1)[1].strip()
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
    elif command.find("-N") >= 0:
        message = command.split(sep="-N", maxsplit=1)[0].strip()
        friend_name = command.split(sep="-N", maxsplit=1)[1].strip()
    # not specified TO, set as default
    else:
        message = command
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
    return message, friend_name


def show_help():
    "print help guide in terminal"
    print("""
  Command
    h                        Show this help guide
    REFRESH                  Refresh friends list
    all                      List all WeChat friends of this account
    ls                       List the last 5 WeChat contacts of this accound
    q                        Log out
    f <keywords>             Search friends by keywords
    re <message>             Send a message to the last FROM (you receive msg from)
    s <message>              Send a message to the last TO (you send msg to)
    s <message> -N <name>    Send a message to a friend specified by name
    s <message> -n <num>     Send a message to a friend specified by num
    s @fil@<filename>        Send a file (@img@ for image, @vid@ for video)
    """)
