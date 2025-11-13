# syntax highlighting 
print("")

# detail code

# revision
age = 30
name = "name"
# print(f"My name is {name} and I am {age} years old.")
print(name)
print(age)

# two print function to print in same line
print(name, end=" ") # end = " "
print(age)

# syntax of while loop
i = 1
while i <= 5:
    print(i)
    i += 1

# small game to guess a number using while loop
secret_number = 7
heath = 3

number = int(input("Guess the secret number between 1 and 10: "))

while number != secret_number:
    print("Wrong guess! Try again.")
    # heath = heath - 1
    heath -= 1
    if heath <= 0:
        print("Game Over! You've used all your attempts.")
        exit()
    print(f"You have {heath} attempts left.")
    number = int(input("Guess the secret number between 1 and 10: "))

print("Congratulations! You guessed the correct number.")


# lists
numbers = [1, 2, 3, 4, 5]
print(numbers)
print(type(numbers))
print(numbers[2])

for number in numbers:
    print(number, end=" ")


languages = ['Swift', 'Python', 'Go']

# start of the loop
for lang in languages:
    print(lang)
    print('-----')
# end of the for loop

print('Last statement')

# print 1 to 10 except 5

for i in range(1, 11):
    if i == 5:
        continue
    print(i, end=" ")

for i in range (1, 11):
    if i!=5:
        print(i, end=" ")

