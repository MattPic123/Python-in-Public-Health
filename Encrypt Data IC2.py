# Data Anonymization Lab - IC Assignment
# Name: Matt Picaroni
# Purpose: Store sample patient profile information, allow users to
#/query profile data, encrypt the profile data, and save the/
#/encrypted information to a file.

from datetime import date
from anonymate.anonymizer import Anonymizer

# Create the Anonymizer object
anonymizer = Anonymizer()


# Profile Data

profiles = [
    {
        'name': 'Oscar Newman',
        'sex': 'M',
        'DoB': date(1927, 1, 19),
        'blood_type': 'B+'
    },
    {
        'name': 'Jeremy Wilson',
        'sex': 'M',
        'DoB': date(1996, 10, 12),
        'blood_type': 'A-'
    },
    {
        'name': 'Kenneth Rhodes',
        'sex': 'M',
        'DoB': date(2003, 6, 15),
        'blood_type': 'A-'
    },
    {
        'name': 'Nicole Richardson',
        'sex': 'F',
        'DoB': date(2003, 9, 7),
        'blood_type': 'AB+'
    },
    {
        'name': 'Gary Gamble',
        'sex': 'M',
        'DoB': date(1968, 8, 19),
        'blood_type': 'A+'
    }
]


# Encrypt Profile Data

def encrypt_profiles():

    encrypted_profiles = []

    # Encrypt each profile
    for profile in profiles:

        data = (
            f"Name: {profile['name']}, "
            f"DoB: {profile['DoB']}, "
            f"Sex: {profile['sex']}, "
            f"Blood Type: {profile['blood_type']}"
        )

        encrypted_data = anonymizer.encrypt_text(data)

        encrypted_profiles.append(encrypted_data)

    # Save the encrypted profiles to a text file
    with open("encrypted_profiles.txt", "w") as file:

        for encrypted_profile in encrypted_profiles:
            file.write(str(encrypted_profile) + "\n")

    print("\nProfile data has been encrypted successfully.")
    print("Encrypted data saved to encrypted_profiles.txt")

    return encrypted_profiles


# Query Profile Data

def query_profiles():

    print("\nWhat information would you like to query?")
    print("1. Name")
    print("2. DoB")
    print("3. Sex")
    print("4. Blood Type")

    choice = input("\nEnter your choice: ")

    # Display names
    if choice == "1":

        for profile in profiles:
            print(profile['name'])

    # Display dates of birth
    elif choice == "2":

        for profile in profiles:
            print(profile['DoB'])

    # Display sex
    elif choice == "3":

        for profile in profiles:
            print(profile['sex'])

    # Display blood types
    elif choice == "4":

        for profile in profiles:
            print(profile['blood_type'])

    else:
        print("Invalid choice.")


# Main Program

def main():

    encrypted_profiles = None

    while True:

        print("\nProfile System")
        print("1. Query profile information")
        print("2. Encrypt profile data")
        print("3. Exit")

        choice = input("\nSelect an option: ")

        # Query profile information
        if choice == "1":

            query_profiles()

        # Encrypt and save profile information
        elif choice == "2":

            encrypted_profiles = encrypt_profiles()

        # Exit the program
        elif choice == "3":

            print("Seeya!")
            break

        else:

            print("Invalid choice. Please try again.")


# Run the program

if __name__ == "__main__":
    main()
