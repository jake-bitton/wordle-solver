def format_words(read_file, write_file='previous_words.txt'):
    f = open(read_file, 'r')
    words = f.read().strip().split()
    f.close()
    w = open(write_file, 'a')
    for word in words:
        w.write(word.lower() + '\n')
    w.close()
    print(f'Formatted words in {read_file}, wrote to {write_file}')


def main():
    format_words('used_words.txt', 'word_lists\\previous_words.txt')


if __name__ == '__main__':
    main()
