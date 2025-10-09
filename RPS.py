import random

def get_user_choice():
     print("Choose one: [R]ock, [P]aper, [S]cissors")
     user_choice = input("Your choice: ").upper()

     while user_choice not in ['R', 'P', 'S']:
          print("Invalid input, please choose 'R', 'P', or 'S'.")
          user_choice = input("Your choice: ").upper()

     return user_choice

def get_computer_choice():
     choices = ['R', 'P', 'S']
     return random.choice(choices)

def determine_winner(user_choice, computer_choice):
     if user_choice == computer_choice:
          return "It's a tie!"
     elif (user_choice == 'R' and computer_choice == 'S') or \
         (user_choice == 'P' and computer_choice == 'R') or \
         (user_choice == 'S' and computer_choice == 'P'):
          return "You win!"
     else:
          return "Computer wins!"

def display_choices(user_choice, computer_choice):
     choices = {'R': 'Rock', 'P': 'Paper', 'S': 'Scissors'}
     print(f"You chose: {choices[user_choice]}")
     print(f"Computer chose: {choices[computer_choice]}")

def play_game():
     print("Welcome to Rock, Paper, Scissors!")

     while True:
          user_choice = get_user_choice()
          computer_choice = get_computer_choice()

          display_choices(user_choice, computer_choice)
          result = determine_winner(user_choice, computer_choice)
          print(result)

          play_again = input("Do you want to play again? (yes/no): ").lower()
          if play_again != 'yes':
               break

     print("Thanks for playing!")

# Start the game
if __name__ == "__main__":
     play_game()
