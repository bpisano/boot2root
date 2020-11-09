alphabet = "abcdefghijklmnopqrstuvwxyz"
weird_alphabet = "isrveawhobpnutfg"
target_word = "giants"

def weird_letter_for_letter(letter):
    weird_letter_index = ord(letter) & 0xf
    return weird_alphabet[weird_letter_index]

password = ""

for target_word_letter in target_word:
    for alphabet_letter in alphabet:
        weird_alphabet_letter = weird_letter_for_letter(alphabet_letter)
        if weird_alphabet_letter == target_word_letter:
            password += alphabet_letter
            break

print(password)