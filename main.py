# -*- coding: utf-8 -*-

from os import system, path
import _thread
import logging

import pickle
import itchat
from itchat.content import *
from termcolor import cprint, colored
from pyfiglet import Figlet

from utils import *

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

f_lock = _thread.allocate_lock()


@itchat.msg_register(itchat.content.TEXT)
def debug_msg(msg):
    "monitor new message to call this function and show all info of message"
    print(msg)


def cmd_ctrl():
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
        save_var(username, [last_from, last_to], [all_friends, recent_friends])
        itchat.logout()
        custom_fig = Figlet(font='basic')  # whimsy / contessa / basic
        print(custom_fig.renderText('Bye'))
    elif command_ == "ls":
        show_list(recent_friends, all_friends)
        print()
    elif command_ == "all":
        show_list(all_friends, all_friends)
        print()
    elif command.startswith("f"):
        find_friend(command, all_friends)
        print()
    elif command.startswith("s") or command.startswith("re"):
        m, n = send_format(command, last_from, last_to)
        send_msg(m, n)
        print()
    else:
        print("[lol] Invalid Input!")


def launcher_loop():
    "get command from terminal"
    custom_fig = Figlet(font='basic')  # whimsy / contessa / basic
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
    "update friends list's order"
    global all_friends, recent_friends
    # lock data to ensure atomicity
    f_lock.acquire()

    # insert last friend name to front of list
    if friend_name in recent_friends:
        recent_friends.remove(friend_name)
    recent_friends.insert(0, friend_name)

    if friend_name in all_friends:
        all_friends.remove(friend_name)
    all_friends.insert(0, friend_name)

    # control recent list length
    if len(recent_friends) > 10:
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
            if all_friends:
                update_friends(friend_name)
            global last_to
            last_to = friend_name


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
    if all_friends:
        update_friends(friend_name)
    global last_from
    last_from = friend_name


@itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO])
def download_files(msg):
    global last_from
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
    if all_friends:
        update_friends(friend_name)
    last_from = friend_name


def save_var(username, last, friends):
    with open('./stuff.pkl', 'wb') as f:
        pickle.dump(username, f)
        pickle.dump(last, f)
        pickle.dump(friends, f)


# Main
logging.disable(logging.DEBUG)  # disable itchat debug log
_thread.start_new_thread(launcher_loop, ())  # call launcher loop
itchat.auto_login(hotReload=True)
itchat.run(True)
