import os
import pyfiglet
import time
from cyoa_classes import Game, Story, Player
from openai import OpenAI
import json

client = OpenAI()

def main():
    opening_screen()
    game, story, player = game_choices_setup()



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

def game_choices_setup():
    """Gathers the information necessary to start the game"""
    game = Game()
    print('What is your name, player? ')
    player_name = input()
    print(f'Thank you, {player_name}. What is your gender? ')
    player_gender = input()
    print("And what species are you? (You'll get better results if you pick something that can move and speak!) ")
    player_species = input()
    player = Player(player_gender, player_species, player_name)
    print("Do you want to pick the type of story and the setting, or do you want it to be a surprise? Enter 1 to choose or 2 to be surprised. ")
    choice = int(input())
    while choice != 1 and choice != 2:
        print("Please enter 1 to choose the story, or 2 to be surprised. ")
        choice = int(input())
    if choice == 1:
        print('What is the topic or genre for the story you want to play? ')
        story_topic = input()
        print('What is the time period? ')
        story_time_period = input()
        print('What is the setting for the story? ')
        story_setting = input()
        story = Story(story_topic, story_time_period, story_setting)
    else:
        story = generate_story_prompt()
    return game, story, player


def generate_story_prompt():
        """Calls OpenAI to generate a semi-random story topic, setting, and time period."""
        try:
            response = client.chat.completions.create(model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a creative writing assistant who generates random but compelling storytelling settings."},
                {"role": "user", "content": "Generate a unique story concept with a topic/genre, an interesting setting, and a time period. Return it in JSON format like this: {'topic': '...', 'setting': '...', 'time_period': '...'}"}
            ])
            # Extract the AI-generated JSON string
            raw_text = response.choices[0].message.content
            raw_text.replace("'", '"')
            print(raw_text)

            # Convert JSON-like text into a dictionary 
            story_data = json.loads(raw_text)

            # Create a new Story instance using the generated data
            return Story(
                topic=story_data["topic"], 
                setting=story_data["setting"], 
                time_period=story_data["time_period"])


        except json.JSONDecodeError as e:
            print("Error parsing JSON: ", e)
            print("Response was ", raw_text)
            
        except Exception as e:
            print("Error generating story:", e)



if __name__ == "__main__":
    main()