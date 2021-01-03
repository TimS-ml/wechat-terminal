import time


def get_time():
    "get time and format it"
    return time.strftime('%H:%M:%S')


def show_list(friends, all_friends):
    "show friends list"
    if all_friends:
        for index, friend_name in enumerate(friends):
            index += 1
            print(f"{index}. {friend_name}\t", end="")
    else:
        print("No friend in this list")


def find_friend(command, all_friends):
    "filter friends by kws"
    kws = command.strip("f").strip()
    for key, friend_name in enumerate(all_friends):
        if kws in friend_name:
            print(key + 1, friend_name)


def send_format(command, last_from, last_to):
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