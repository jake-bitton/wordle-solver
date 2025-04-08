class WordleSolver:
    def __init__(self, all_wordlist, previous_wordlist = 'word_lists\\used_words.txt', guesses=None):

        self.answer = {1: '', 2: '', 3: '', 4: '', 5: ''}
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

    def add_guess(self, guess: str, known_letters: list = None, wrong_letters: list = None, correct_letters: dict = None):
        assert len(guess) == 5

        if (guess not in self.used_wordlist) and (guess not in self.guesses):
            self.guesses.append(guess.lower())

        self.update_answer(correct_letters)
        self.update_letters(known_letters, wrong_letters)

        for word in self.possible_words:
            for letter in word.split():
                if letter in self.excluded_letters:
                    self.possible_words.remove(word)


    def update_answer(self, correct_letters: dict = None):
        if correct_letters is not None:
            self.answer.update(correct_letters)
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
        '''
        based on possible words list and used words list as well as known letters and answer,
        compares possible words (excluding used words)
        :return:
        '''

    def __str__(self) -> str:
        return f'Guesses: {self.guesses}\nYou have {5 - len(self.guesses)} guesses remaining.\nKnown letters: {self.known_letters}\nExcluded letters: {self.excluded_letters}\nAnswer so far: {self.answer}'

def main():
    wordle_solver = WordleSolver('word_lists\\all_possible_words.txt')
    wordle_solver.add_guess('brain', ['B','r','u'], ['a', 'i'], {1: 'b', 2: 'r'})
    print(wordle_solver)


if __name__ == '__main__':
    main()