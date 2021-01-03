from termcolor import colored
from colorama import init, Fore, Back, Style
init()

username = 'lol'

print(
    f"\n{username} received\n",
    end='')
print(Fore.YELLOW + "~> " + Style.RESET_ALL)
