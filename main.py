import os
import pyfiglet
import time
from openai import OpenAI

def main():
    opening_screen()

def opening_screen():
    """Display screen for start of game"""
    clear_terminal()
    width = 80 # related to width of screen, probably 80-120
    title = "Choose Your Own Adventure - Artificial Intelligence Edition"
    ascii_title = pyfiglet.figlet_format(title) #creates ascii art of my title
    print('*' * width)
    print(ascii_title)
    print('*' * width)
    time.sleep(5)
    print('Welcome to Choose Your Own Adventure - Artificial Intelligence Edition!')
    print('In this game, you will make the choices that determine what happens next.')
    print('Your choices, plus some prompts from the storyline, will generate a unique storyline each time you play.')
    time.sleep(5)
    clear_terminal()



def clear_terminal():
    """Clears the terminal screen when called"""
    os.system('cls' if os.name == 'nt' else 'clear')


if __name__ == "__main__":
    main()