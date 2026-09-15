import json
import os
from faker import Faker
from anonymate.anonymizer import Anonymizer
from cryptography.fernet import Fernet

# Load or create a persistent encryption key
key_file = "encryption.key"

if os.path.exists(key_file):
    with open(key_file, "rb") as file:
        key = file.read()
else:
    key = Fernet.generate_key()
    with open(key_file, "wb") as file:
        file.write(key)

# Initialize the Faker engine and Anonymizer engine
fake = Faker()
anonymizer = Anonymizer()

# faker_len function
def faker_len(length):
    data = []

    for _ in range(length):
        data.append(fake.name())

    return data

# Prompt user for data length
data_length = int(input("How many patient profiles would you like to create?"))

# Initialize Data Variable
data = []

# Call faker_len function to generate names
data = faker_len(data_length)

# Print data to terminal
print(data)

# Turning data into a string
data_str = json.dumps(data, default=str)

# Run anonymizer
encrypted_data_str = anonymizer.encrypt_text(data_str)

# Show encrypted data to user
print(encrypted_data_str)