import Levenshtein
import pandas as pd
from pandas import DataFrame


class WordleSolver:
    def __init__(self, all_wordlist, previous_wordlist = 'word_lists\\used_words.txt', guesses=None):

        self.answer = '-----'
        self.known_letters = list()
        self.excluded_letters = list()

        if guesses is None:
            guesses = []
        self.guesses = guesses

        try:
            with open(all_wordlist, 'r') as f:
                self.all_wordlist = f.read().splitlines()
        except FileNotFoundError:
            raise FileNotFoundError(f"File {all_wordlist} not found.")
        finally:
            f.close()

        try:
            with open(previous_wordlist, 'r') as f:
                self.used_wordlist = f.read().splitlines()
        except FileNotFoundError:
            raise FileNotFoundError(f"File {previous_wordlist} not found.")
        finally:
            f.close()

        self.possible_words = list()
        for word in self.all_wordlist:
            if word not in self.used_wordlist:
                self.possible_words.append(word)

    def add_guess(self, guess: str, known_letters: list = None, wrong_letters: list = None, correct_letters: str = None):
        assert len(guess) == 5

        if (guess not in self.used_wordlist) and (guess not in self.guesses):
            self.guesses.append(guess.lower())

        self.update_answer(correct_letters)
        self.update_letters(known_letters, wrong_letters)

        for word in self.possible_words:
            for letter in word:
                if letter in self.excluded_letters:
                    try:
                        self.possible_words.remove(word)
                        print(f'Removed {word} from possible words. (add_guess, contains excluded letter)')  # For Testing Purposes
                    except ValueError:
                        continue

        for letter in self.known_letters:
            for word in self.possible_words:
                if letter not in word:
                    try:
                        self.possible_words.remove(word)
                        print(f'Removed {word} from possible words. (add_guess, does not contain included letter)') # For Testing Purposes
                    except ValueError:
                        continue


    def update_answer(self, correct_letters: str = None):
        curr_answer_list = self.answer.split('')
        if correct_letters is not None:
            correct_list = correct_letters.split('')
            for letter in correct_list:
                if letter != '-':
                    curr_answer_list[correct_list.index(letter)] = letter
            self.answer = ''.join(curr_answer_list)
            print(f'Updated answer to: {self.answer}')
        else:
            print(f'No values to update in answer.')

    def update_letters(self, known_letters: list = None, wrong_letters: list = None):
        if known_letters is not None:
            for letter in known_letters:
                if letter not in self.known_letters:
                    self.known_letters.append(letter.lower())
            print(f'Updated known letters to: {self.known_letters}')
        else:
            print(f'No values to update in known letters.')
        if wrong_letters is not None:
            for letter in wrong_letters:
                if letter not in self.excluded_letters:
                    self.excluded_letters.append(letter.lower())
            print(f'Updated excluded letters to: {self.excluded_letters}')
        else:
            print(f'No values to update in excluded letters.')

    def make_guess(self):
        """
        OLD:
        based on possible words list and used words list as well as known letters and answer,
        compares possible words (excluding used words) with known letters and known letters in answer
        and returns a list of possible guesses (unordered).

        NEW:
        based on partial answer, returns top 5 most likely answers based on results of compare()ing
        answer to all words in possible_words.
        """
        most_likely = list()
        compared = self.compare()
        for i in range(5):
            most_likely.append(compared.Comparisons.get(i))
        return most_likely


        #   Deprecated
        guess = self.possible_words
        full_answer = ''
        for char in self.answer:
            full_answer += self.answer.get(char)
        if full_answer == '':
            return guess
        else:
            for word in self.possible_words:
                for i, letter in enumerate(word.split()):
                    if self.answer.get(i) != '' and letter != self.answer.get(i):
                        self.possible_words.remove(word)
                        print(f'Removed {word} from possible guesses.(make_guess)') # For Testing Purposes
            return guess


    def take_input(self):
        guess = input('Guess: ')
        assert len(guess) == 5
        known_letters = list(input("Enter known letters (space delimited): ").split())
        wrong_letters = list(input("Enter wrong letters (space delimited): ").split())
        known_positions = list(input("Enter known positions (space delimited): ").split())
        temp_answer = self.answer.copy()
        for num in known_positions:
            if temp_answer.get(int(num)) == '':
                temp_answer[int(num)] = guess[int(num)-1].lower()
        # Above 4 lines need to be updated to work with self.answer being a string.
        print(f'Known letters: {known_letters}\nWrong letters: {wrong_letters}\nKnown positions: {known_positions}\nAnswer: {temp_answer}')
        #   Above line is for testing purposes
        self.add_guess(guess, known_letters, wrong_letters, temp_answer)
        print(f'Added guess: {guess}')

    def check_answer(self):
        answer_word = ''
        for char in self.answer:
            if char == '':
                return False
            else:
                answer_word += self.answer.get(char) # Update to work with self.answer as string.
        if answer_word in self.possible_words:
            return True

    def compare(self, guess: str = None, compare_vals: list[str] = None) -> DataFrame:
        """
        Takes in a guess and a list of comparison values and calculates the levenshtein distance
        between the two and returns a dataframe ordered by highest to lowest distance between guess
        and comparison value

        :param compare_vals: list[str] of values to compare against guess to find most similar
        :param guess: 5 char string (with unknowns as -) to compare against list of comparison values
        :return percent_similar: DataFrame
        """
        if guess is None:
            guess = ''
            for v in self.answer:
                if v == '':
                    guess += '-'
                else:
                    guess += self.answer.get(v) # Update to work with self.answer as a string.
        if compare_vals is None:
            compare_vals = self.possible_words

        compare_vals.insert(0, guess)
        percent_similar = pd.DataFrame()
        percent_similar['Comparisons'] = compare_vals
        percent_similar['Similarity'] = Levenshtein.ratio(guess, percent_similar['Comparisons'])
        percent_similar.sort_values(by='Comparisons', ascending=False, inplace=True)
        return percent_similar


    def __str__(self) -> str:
        return f'Guesses: {self.guesses}\nYou have {6 - len(self.guesses)} guesses remaining.\nKnown letters: {self.known_letters}\nExcluded letters: {self.excluded_letters}\nAnswer so far: {self.answer}\nPossible words: {self.make_guess()}'

def main():
    wordle_solver = WordleSolver('word_lists\\all_possible_words.txt')
    while not wordle_solver.check_answer():
        wordle_solver.take_input()
        print(wordle_solver.make_guess())
        print(wordle_solver)



if __name__ == '__main__':
    main()