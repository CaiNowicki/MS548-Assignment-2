#This file will contain the classes for my CYOA game
import random

class Story:
#Tracks the story topic, prompts, and responses
    def __init__(self, topic, setting, time_period):
        self.topic = topic
        self.setting = setting
        self.time_period = time_period
        self.prompt_response_dict = {}
        #this is for the developer role in the API call
        self.narrator_type = random.choice(['cheery', 'somber', 'formal', 'mysterious', 'fantastical', 'scientific', 'comedic', 'satirical'])
                

class Player:
    #tracks player attributes
    def __init__(self, gender, species, name):
        self.gender = gender
        self.species = species
        self.name = name
        self.inventory = []
        self.skills = []
        self.choices = []

#Breaking this up into separate spots in the classes means that I can store just the parts of the prompts that change
#I can prompt every time with the character's name, gender etc. but I don't have to store that part in the prompt_response dictionary
#this will also help prevent false positives when checking for similarity in responses (to avoid a character going in circles)


class Game:
    #keeps track of the state of the game and handles API calls
    def __init__(self):
        self.current_state = None
        self.chapters = 0

    def start_story():
        #first API call to set up story
        #use OpenAI quickstart guide here
        pass
    
    def show_choices():
        #display the choices for the user's next actions on the screen
        #then take those responses and send them on to the next step for generative text
        pass

    def update_state():
        #add result of choices to current_state and increment chapters
        pass
