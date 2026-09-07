# Patient Heart Rate Directory

heart_rate_samples = {
    "J. Alvarez": [72, 75, 78],
    "M. Chen": [80, 82],
    "R. Okafor": [65, 68, 70, 66],
    "S. Patel": [90, 95, 92, 88, 91],
    "T. Nguyen": [77, 79],
    "L. Kowalski": [68, 70, 69],
    "D. Osei": [98, 101, 95, 99],
    "A. Whitfield": [74, 76, 75, 73]
}


# Retrieving patient data
def get_patient(patient_number, *args):
    patients = list(args[0].keys())

    if patient_number < 1 or patient_number > len(patients):
        return None

    patient_name = patients[patient_number - 1]
    return patient_name, args[0][patient_name]


# Calculate and display patient statistics
def patient_stats(patient_name, samples, *args):
    print("\nPatient:", patient_name)
    print("Heart rate samples:", samples)
    print("Minimum Heart Rate:", min(samples))
    print("Maximum Heart Rate:", max(samples))
    print("Average Heart Rate:", sum(samples) / len(samples))


# Display all patient information
def display_all_patients(data, *args):
    for patient_number, (patient_name, samples) in enumerate(data.items(), start=1):
        print("\nPatient Number:", patient_number)
        patient_stats(patient_name, samples)


# Main Program
while True:

    print("\nPatient Heart Rate Directory")
    print("1. Retrieve all patient stats")
    print("2. Retrieve specific patient stats")
    print("3. Exit")

    choice = int(input("Enter your choice: "))

    # Retrieve all patient information
    if choice == 1:
        display_all_patients(heart_rate_samples)

    # Retrieve specific patient information
    elif choice == 2:

        print("\nPatient Numbers:")

        for number, name in enumerate(heart_rate_samples.keys(), start=1):
            print(number, "-", name)

        patient_number = int(input("\nEnter patient number: "))

        result = get_patient(patient_number, heart_rate_samples)

        if result is None:
            print("\nNo patient found.")

        else:
            patient_name, samples = result

            print("\nWhat information do you want?")
            print("1. All patient info")
            print("2. Heart rate samples")
            print("3. Minimum Heart Rate")
            print("4. Maximum Heart Rate")
            print("5. Average Heart Rate")

            stat_choice = int(input("Enter your choice: "))

            if stat_choice == 1:
                patient_stats(patient_name, samples)

            elif stat_choice == 2:
                print("Heart Rate Samples:", samples)

            elif stat_choice == 3:
                print("Minimum Heart Rate:", min(samples))

            elif stat_choice == 4:
                print("Maximum Heart Rate:", max(samples))

            elif stat_choice == 5:
                average = sum(samples) / len(samples)
                print("Average Heart Rate:", average)

            else:
                print("Invalid statistic choice.")

    # Exit program
    elif choice == 3:
        print("Exiting Program...")
        break

    else:
        print("Invalid choice. Enter 1, 2, or 3.")

