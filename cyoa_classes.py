#This file will contain the classes for my CYOA game
import random
import os
from openai import OpenAI
from dotenv import load_dotenv
import json
import re


# Load environment variables from .env
load_dotenv()

# Retrieve the API key
api_key = os.getenv("OPENAI_API_KEY") 

client = OpenAI(api_key=api_key)

class Story:
#Tracks the story topic, prompts, and responses
    def __init__(self, topic, setting, time_period):
        self.topic = topic
        self.setting = setting
        self.time_period = time_period
        self.prompt_response_dict = {}
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
        self.generate_text("You find yourself in a strange place...") #real text for API call goes here later

    def show_choices(self, choices):
        """Display choices and allow the player to pick one."""
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
        self.current_state += f" {choice}"  # Append choice to state
        self.generate_text(f"After choosing to {choice.lower()}, you experience...")

    def generate_text(self, prompt):
        """Call OpenAI API to generate story text based on the current state."""
        try:
            response = client.chat.completions.create(model="gpt-4",
            messages=[
                {"role": "system", "content": f"You are a {self.story.narrator_type} storyteller. Generate a short story continuation and a set of 2-3 logical choices based on the given input. The main character is {self.player.name}, a {self.player.gender} {self.player.species}. Write the story in 2nd person (you) perspective. It should be possible for the main character to get hurt or even die (which ends the narrative) based on the choices."},
                {"role": "user", "content": f"{self.current_state} {prompt}.  Provide output in JSON format: {{\"story\": \"...\", \"choices\": ['...', '...']}}. Provide only the JSON object and no other text content. Within the text of the story and choices objects, do not use any quotation marks."}
            ])
            raw_text = response.choices[0].message.content
            # This regex changes the single quotes in the content to double quotes for JSON but only around the keys and values
            raw_text = re.sub(r"(\w+)(:)", r'"\1"\2', raw_text)  # Add quotes around keys
            raw_text = re.sub(r'(":?)\s*\'(.*?)\'\s*', r'\1"\2"', raw_text)  # Convert single quotes to double quotes for values

            try:
                        story_data = json.loads(raw_text)
                        generated_text = story_data["story"]
                        choices = story_data["choices"]

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
        
        if not story_text:
            print("Error generating story content.")
            return
        
        print(story_text)

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
        
        # Increment chapter count
        self.chapters += 1

