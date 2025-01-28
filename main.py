import os
import pyfiglet

def main():
    opening_screen()

def opening_screen():
    clear_terminal()
    width = 80 # related to width of screen, probably 80-120
    title = "Choose Your Own Adventure - Artificial Intelligence Edition"
    ascii_title = pyfiglet.figlet_format(title) #creates ascii art of my title
    print('*' * width)
    print(ascii_title)
    print('*' * width)




def clear_terminal():
    """Clears the terminal screen when called"""
    os.system('cls' if os.name == 'nt' else 'clear')


if __name__ == "__main__":
    main()