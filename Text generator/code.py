from random import choice, choices
from nltk.tokenize import WhitespaceTokenizer
from collections import defaultdict, Counter
import re


class TextGenerator:

    def __init__(self):
        self.path = input()
        self.tokens = self.tokens()
        self.ngrams = self.ngrams()

    def read_file(self):
        with open(self.path, encoding="utf-8") as file:
            text = file.read()
        return text

    def tokens(self):
        text = self.read_file()
        tk = WhitespaceTokenizer()
        return tk.tokenize(text)

    def ngrams(self):
        ngrams = defaultdict(Counter)
        for i in range(len(self.tokens) - 2):
            ngrams[" ".join(self.tokens[i:i + 2])].update((self.tokens[i + 2],))
        return ngrams

    def find_start(self):
        """method is used to find the first words of the sentence"""
        reg = r"^[A-Z]{1}[^\.\!\?]*?$"
        starts = [word for word in list(self.ngrams) if re.match(reg, word.split()[0])]
        return choice(starts).split()

    def make_sentence(self, n=5):
        """main method of the script. It randomly chooses the next words in
        sentence accordingly to their weight in the original text and returns the new sentence"""
        result = []
        while True:
            if len(result) == 0:
                result = self.find_start()
            w1 = " ".join(result[-2:])
            w2 = choices(list(self.ngrams[w1].keys()), list(self.ngrams[w1].values()))
            result.append(*w2)

            if w2[0][-1] in ".!?":
                if len(result) < n:
                    result = []
                    continue
                return " ".join(result)


if __name__ == "__main__":
    text_gen = TextGenerator()
    for _ in range(10):
        print(text_gen.make_sentence())
