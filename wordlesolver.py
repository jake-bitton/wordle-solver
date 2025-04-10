import Levenshtein
import pandas as pd
from pandas import DataFrame
import re


class WordleSolver:
    def __init__(self, all_wordlist, previous_wordlist='word_lists\\used_words.txt', guesses=None):

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
        self.possible_words.sort()

    def add_guess(
            self,
            guess: str,
            known_letters: list = None,
            wrong_letters: list = None,
            correct_letters: str = None):
        assert len(guess) == 5

        if (guess not in self.used_wordlist) and (guess not in self.guesses):
            self.guesses.append(guess.lower())

        self.update_answer(correct_letters)
        self.update_letters(known_letters, wrong_letters)
        self.possible_words.pop(self.possible_words.index(guess))

        for word in self.possible_words:
            for letter in word:
                if self.excluded_letters.__contains__(letter):
                    try:
                        self.possible_words.remove(word)
                    except ValueError:
                        continue

    def update_answer(self, correct_letters: str = None):
        curr_answer_list = [char for char in self.answer]
        if correct_letters is not None:
            correct_list = [char for char in correct_letters]
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

    def make_guess(self, num_words=5):
        """
        OLD:
        based on possible words list and used words list as well as known letters and answer,
        compares possible words (excluding used words) with known letters and known letters in answer
        and returns a list of possible guesses (unordered).

        NEW:
        based on partial answer, returns top 5 most likely answers based on results of compare()ing
        answer to all words in possible_words.
        """

        compared = self.compare()
        most_likely = self.drop_invalid_rows(compared)
        return most_likely[0:num_words]

    def take_input(self):
        guess = input('Guess: ')
        assert len(guess) == 5
        known_letters = list(input("Enter known letters (space delimited): ").split())
        wrong_letters = list(input("Enter wrong letters (space delimited): ").split())
        known_positions = list(input("Enter known positions (space delimited): ").split())
        temp_answer = [char for char in self.answer]
        for num in known_positions:
            if temp_answer[int(num)-1] == '-':
                temp_answer[int(num)-1] = guess[int(num)-1].lower()
        temp_answer = ''.join(temp_answer)
        print(
            f'Known letters: {known_letters}\nWrong letters: {wrong_letters}\nKnown positions: {known_positions}\nAnswer: {temp_answer}'
        )
        #   Above line is for testing purposes
        self.add_guess(guess, known_letters, wrong_letters, temp_answer)
        print(f'Added guess: {guess}')

    def check_answer(self):
        answer_word = ''
        for i, char in enumerate(self.answer):
            if char == '-':
                return False
            else:
                answer_word += self.answer[i]
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
            guess = self.answer
        if compare_vals is None:
            compare_vals = self.possible_words

        ratios = list()
        for val in compare_vals:
            ratios.append(Levenshtein.ratio(guess, val))
        percent_similar = pd.DataFrame()
        percent_similar['Comparisons'] = compare_vals
        percent_similar['Similarity'] = ratios
        percent_similar.sort_values(by='Similarity', ascending=False, inplace=True)
        return percent_similar

    def drop_invalid_rows(self, df):
        """
        Drops rows from the DataFrame where any string value contains an excluded character.

        Parameters:
        df (pd.DataFrame): The input DataFrame.

        Returns:
        pd.DataFrame: DataFrame with rows containing excluded characters removed.
        """
        # Create a copy to avoid modifying the original DataFrame
        df = df.copy()

        # Handle case with no excluded or included characters
        if not self.excluded_letters and not self.known_letters:
            return df

        # Identify string columns (object or string dtype)
        string_cols = df.select_dtypes(include=['object', 'string']).columns.tolist()

        # Initialize a boolean mask for rows to exclude (default False)
        mask_excluded = pd.Series(False, index=df.index)
        mask_missing_included = pd.Series(False, index=df.index)
        mask_missing_in_place = pd.Series(False, index=df.index)

        # Process excluded characters
        if self.excluded_letters:
            # Create regex pattern to match any excluded character
            excluded_pattern = r'[{}]'.format(''.join(re.escape(c) for c in self.excluded_letters))

            for col in string_cols:
                # Check if the column contains any excluded characters
                mask_excluded |= df[col].str.contains(excluded_pattern, na=False, regex=True)

        # Process included characters
        if self.known_letters:
            # Create regex pattern to ensure all included characters are present
            included_pattern = r'^'
            for c in self.known_letters:
                included_pattern += r'(?=.*{})'.format(re.escape(c))
            included_pattern += r'.*'

            for col in string_cols:
                # Check if the column does NOT contain all included characters
                mask_missing_included |= ~df[col].str.contains(included_pattern, na=False, regex=True)

        # Process characters in known positions
        answer_list = [char if char != '-' else None for char in self.answer]
        # Construct the regex pattern based on check_list
        pattern_parts = []
        for char in answer_list:
            if char is not None:
                # Escape special regex characters
                pattern_parts.append(re.escape(char))
            else:
                # Allow any character at this position
                pattern_parts.append('.')
        # Combine parts into regex pattern
        regex_pattern = '^' + ''.join(pattern_parts)

        # Create the mask using str.match, handling NaN values as False
        for col in string_cols:
            mask_missing_in_place = ~df[col].str.match(regex_pattern, na=False, case=False)

        # Create a final mask with all masks
        final_mask = mask_excluded | mask_missing_included | mask_missing_in_place

        # Return DataFrame excluding rows where any string column contains excluded characters
        return df[~final_mask]

    def __str__(self) -> str:
        return f'Guesses: {self.guesses}\nYou have {6 - len(self.guesses)} guesses remaining.\nKnown letters: {self.known_letters}\nExcluded letters: {self.excluded_letters}\nAnswer so far: {self.answer}'


def main():
    wordle_solver = WordleSolver('word_lists\\all_possible_words.txt')

    while not wordle_solver.check_answer():
        wordle_solver.take_input()
        print(wordle_solver.make_guess())
        print(wordle_solver)


if __name__ == '__main__':
    main()
