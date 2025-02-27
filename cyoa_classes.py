#This file will contain the classes for my CYOA game
import random
import os
import json
import re
import sys
import requests

class Tee:
    '''This is a custom class that will output print() statements to the terminal
    while simultaneously logging them to a file.'''
    def __init__(self, filename):
        self.file = open(filename, "w+")
        self.stdout = sys.stdout #save the original stdout

    def write(self, message):
        self.file.write(message) #write the message to the file
        self.stdout.write(message) #display message on console
    
    def flush(self):
        self.file.flush()
        self.stdout.flush()


class Story:
#Tracks the story topic, prompts, and responses
    def __init__(self, topic, setting, time_period):
        self.topic = topic
        self.setting = setting
        self.time_period = time_period
        self.prompt_response_dict = {}  # tracks choices and responses
        #this defines the tone for the API-generated text
        self.narrator_type = random.choice(['cheery', 'somber', 'formal', 'mysterious', 'fantastical', 'scientific', 'comedic', 'satirical'])


class Person:
    """Base class for all characters in the game, including the player character"""
    def __init__(self, gender, species, name, inventory=None):
        self.gender = gender
        self.species = species
        self.name = name
        self.inventory = inventory if inventory is not None else []
        self.currency = 0  #default currency amount
class Player(Person):
    #tracks player attributes, inventory, skills, and story choices
    def __init__(self, gender, species, name, inventory=None, skills=None, choices=None):
        super().__init__(gender, species, name)
        self.inventory = inventory if inventory is not None else []
        self.skills = skills if skills is not None else []
        self.choices = choices if choices is not None else []

class NPC(Person):
    """Represents a non-playable character"""
    def __init__(self, gender, species, name, inventory=None):
        super().__init__(gender, species, name, inventory)
        self.player_reputation = 0 #how the NPC feels about the player
        self.npc_reputation = 0 #how the player feels about the NPC
class Merchant(NPC):
    """A special type of NPC that buys and sells items for currency"""
    def __init__(self, gender, species, name, inventory=None):
        super().__init__(gender, species, name, inventory)
        self.currency = 100 # merchants start with 100 currency

    def list_items(self):
        """Display items for sale"""
        if self.inventory:
            return f"Items for sale: {', '.join(self.inventory)}"
        return "I have nothing for sale right now."

    def sell(self, item, player):
        """Sell an item to a player (move item from merchant to player)"""    
        if item in self.inventory:
            self.inventory.remove(item)
            player.inventory.append(item)
            player.currency -= 10 # using a fixed sale price for simplicity
        return f"I don't have any {item} to sell."

class Game:
    #keeps track of the state of the game and handles API calls
    def __init__(self):
        self.current_state = None
        self.chapters = 0
        self.story = None
        self.player = None
        self.story_state = {} #Tracks last choice and other game state data


    def start_story(self, topic, setting, time_period, player):
        """Initialize the story and make the first API call."""
        self.story = Story(topic, setting, time_period)
        self.player = player
        self.current_state = f"Welcome to {self.story.setting} in {self.story.time_period}."
        self.chapters = 1
        print(self.current_state)
        self.generate_text("You find yourself in a strange place...") 

    def show_choices(self, choices):
        """Display AI generated choices and allow the player to pick one."""
        print("\nWhat do you want to do next?")
        for i, choice in enumerate(choices, start=1):
            print(f"{i}. {choice}")

        while True:
            try:
                selection = int(input("Enter the number of your choice: ")) - 1
                if 0 <= selection < len(choices):
                    return choices[selection]
                print("Invalid choice. Try again.")
            except ValueError:
                print("Please enter a number.")

    def update_state(self, choice):
        """Update the game state with the player's choice."""
        self.chapters += 1
        self.story_state["last_choice"] = choice  # store player's previous choice
        self.generate_text(f"After choosing to {choice.lower()}, you experience...")

    def generate_text(self, prompt):
        """Call Ollama API to generate story text based on the current state."""
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": "llama3", "prompt": f"You are a {self.story.narrator_type} storyteller. Generate a short story continuation based on: {self.current_state} {prompt}. Provide output in JSON format: {{\"story\": \"...\", \"choices\": ['...', '...']}}."},
            )
            raw_text = response.text.strip("`").strip()  #remove markdown backticks

            
            story_data = json.loads(raw_text)
            generated_text = story_data.get("story", "Default Story")
            choices = story_data.get("choices", ["Wait", "Move Forward"]) #get the choices from the JSON object. If it fails, default to those choices.

            # Print story continuation
            print("\n" + generated_text + "\n")

            # Update game state
            self.current_state += " " + generated_text

            return generated_text, choices  # returning the values so the next_chapter() function can access them

        except json.JSONDecodeError as e:
            print("Error parsing JSON: ", e)
            print("Response was: ", raw_text)
            return "An unexpected silence falls over the world...", ["Wait", "Move forward"]

        except Exception as e:
            print("Error generating text:", e)
            return "An eerie quiet settles in as the world pauses...", ["Try again", "Look around"]

    def next_chapter(self):
        """Proceed to the next chapter dynamically based on AI-generated choices."""
        if self.chapters >= 8:
            print("You have reached the end of your journey.")
            return
        
        print(f"\n--- Chapter {self.chapters + 1} ---\n")
        
        # Generate new story content and dynamic choices
        story_text, choices = self.generate_text("What happens next?")
        
        print(story_text)
        if "death" in story_text.lower():
            print("Your story has reached a tragic end. Game over.")
        if self.chapters >= 8:
            print("You realize this adventure is taking up too much of your time and decide to return home. Game over. ")

        # Ensure choices exist before continuing
        if choices:
            print("\nWhat will you do next?")
            for i, choice in enumerate(choices, 1):
                print(f"{i}. {choice}")

            while True:
                try:
                    user_choice = int(input("\nEnter your choice: "))
                    if 1 <= user_choice <= len(choices):
                        break
                    else:
                        print("Invalid choice. Try again.")
                except ValueError:
                    print("Please enter a number corresponding to your choice.")

            # Send the chosen option to the AI for the next chapter
            self.story_state["last_choice"] = choices[user_choice - 1]
        else:
            print("\nNo choices generated, moving forward automatically.")
            self.update_state("Move forward")
        # Increment chapter count
        self.chapters += 1
