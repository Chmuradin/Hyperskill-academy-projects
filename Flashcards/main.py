import json
import random
from collections import defaultdict
import argparse


# Function that returns key from the value of the entry in the dictionary
def get_key(dic: dict, val: str) -> str:
    for key, value in dic.items():
        if val == value:
            return key


class FlashCards:

    def __init__(self):
        self.flashcards = {}
        self.answer = None
        self.user_answer = None
        self.card = None
        self.mistakes = defaultdict(int)
        self.logs = []
        parser: argparse.ArgumentParser = argparse.ArgumentParser(description="Flashcards")
        parser.add_argument("--import_from", help="imports card set")
        parser.add_argument("--export_to", help="exports card set")
        self.args: argparse.Namespace = parser.parse_args()
        if self.args.import_from:
            self.import_card(self.args.import_from)

    def print(self, string=""):
        self.logs.append(string)
        print(string)

    def input(self, string=""):
        self.logs.append(string)
        return input(string)

    def user_menu(self):
        user_command = self.input('Input the action (add, remove, import, export, ask, exit, log, hardest card, '
                                  'reset stats):\n')
        if user_command.lower() == "add":
            self.add_card()
        elif user_command.lower() == "remove":
            self.remove_card()
        elif user_command.lower() == "import":
            self.import_card()
        elif user_command.lower() == "export":
            self.export_card()
        elif user_command.lower() == "ask":
            self.ask_card()
        elif user_command.lower() == "log":
            self.log()
        elif user_command.lower() == "hardest card":
            self.hardest_card()
        elif user_command.lower() == "reset stats":
            self.reset_stats()
        elif user_command.lower() == "exit":
            self.print("Bye bye!")
            if self.args.export_to:
                self.export_card(self.args.export_to)
            exit()
        else:
            pass

    def add_card(self):  # Added Cards
        card = self.input(f"The card:\n")
        while card in self.flashcards:
            self.print(f'The term "{card}" already exists. Try again:')
            card = self.input()

        answer = self.input(f"The definition for card:\n")
        while answer in self.flashcards.values():
            self.print(f'The definition "{answer}" already exists. Try again:')
            answer = self.input()
        self.flashcards[card] = answer
        self.print(f'The pair ("{card}":"{answer}") has been added.')

    def remove_card(self):
        card = self.input('Which card?\n')
        if card in self.flashcards.keys():
            self.flashcards.pop(card)
            self.print('The card has been removed.\n')
        else:
            self.print(f"Can't remove \"{card}\": there is no such card.")

    def import_card(self, file_name=""):
        if file_name == "":
            file_name = self.input('File name:')
        coast = 0
        try:
            with open(file_name, 'r') as card_file:
                json_data = json.load(card_file)
                coast = len(json_data.keys())
                self.flashcards.update(json_data)
        except (FileExistsError, FileNotFoundError):
            self.print('File not found.')
        self.print(f'{coast} cards have been loaded.')

    def export_card(self, file_name=""):
        if file_name == "":
            file_name = self.input('File name:')
        json_data = json.dumps(self.flashcards)
        with open(file_name, 'w') as card_file:
            card_file.write(json_data)
        self.print(f'{len(self.flashcards.keys())} cards have been saved.')

    def ask_card(self):
        card_number = int(self.input("How many times to ask?\n"))
        while card_number > 0:
            rand_card = [random.choice(list(self.flashcards)) for i in range(card_number)]
            for key in rand_card:
                answer = self.input(f'self.Print the definition of "{key}":\n')
                if answer == self.flashcards[key]:
                    self.print("Correct!")
                elif answer in self.flashcards.values():
                    self.mistakes[key] += 1
                    self.print(f'Wrong. The right answer is "{self.flashcards[key]}", but '
                               f'your definition is correct for "{get_key(self.flashcards, answer)}".')
                else:
                    self.mistakes[key] += 1
                    self.print(f'Wrong. The right answer is "{self.flashcards[key]:}".')
                card_number -= 1

    def log(self):
        name = self.input('File name:\n')
        with open(name, 'w') as file:
            file.writelines(self.logs)
        self.print('The log has been saved.')

    def hardest_card(self):
        if self.mistakes.keys() == defaultdict(int).keys():
            self.print("There are no cards with errors.")
        else:
            hardest = max(self.mistakes.items(), key=lambda a: a[1])
            lista = [i for i, j in self.mistakes.items() if j == hardest[1]]
            if len(lista) == 0:
                self.print("There are no cards with errors.")
            if len(lista) == 1:
                self.print(f'The hardest card is "{hardest[0]}". You have {hardest[1]} errors answering it.')
            if len(lista) > 1:
                lista = str(lista)[1:-1].replace("\'", "\"")
                self.print(f'The hardest cards are {lista}. You have {hardest[1]} errors answering them.')

    def reset_stats(self):
        self.mistakes = defaultdict(int)
        self.print("Card statistics have been reset.")

    def main(self):
        while True:
            self.user_menu()
            self.print()


if __name__ == '__main__':
    flash = FlashCards()
    flash.main()
