import json
import os
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

# Gemini API connection
api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    client = genai.Client(api_key=api_key)
else:
    client = None


# Student data file
FILE_NAME = "students.json"


def load_students():
    with open(FILE_NAME, "r") as file:
        data = json.load(file)

    return data["students"]


def save_students(students):
    with open(FILE_NAME, "w") as file:
        json.dump({"students": students}, file, indent=4)


def student_data_tool(roll_number):
    students = load_students()

    for student in students:
        if student["roll_number"] == str(roll_number):
            return student

    return "Student not found."


def calculator_tool(attended, total):
    if total == 0:
        return 0

    return round((attended / total) * 100, 2)


def attendance_tool(roll_number, subject, status):
    students = load_students()

    for student in students:
        if student["roll_number"] == str(roll_number):

            if subject not in student["subjects"]:
                return "Subject not found."

            if status.lower() not in ["present", "absent"]:
                return "Status must be present or absent."

            record = student["subjects"][subject]
            record["total"] += 1

            if status.lower() == "present":
                record["attended"] += 1

            save_students(students)

            percentage = calculator_tool(
                record["attended"],
                record["total"]
            )

            return f"Attendance updated. New percentage: {percentage}%"

    return "Student not found."


def ask_gemini(question):
    if client is None:
        return "Gemini API key not found. Check your .env file."

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=(
                "You are a helpful College AI Assistant. "
                "Answer students in simple English or Hindi. "
                "Be clear and concise.\n\n"
                f"Student question: {question}"
            )
        )

        return response.text

    except Exception as error:
        return f"Gemini connection error: {error}"


# Main program
print("College AI Assistant")
print("--------------------")

roll = input("Enter student roll number: ")
student = student_data_tool(roll)

if isinstance(student, dict):

    print("Student:", student["name"])
    print("Roll Number:", student["roll_number"])

    for subject, record in student["subjects"].items():
        percentage = calculator_tool(
            record["attended"],
            record["total"]
        )

        print(f"{subject}: {percentage}%")

    choice = input("Mark attendance? (yes/no): ")

    if choice.lower() == "yes":
        subject = input("Enter subject name: ")
        status = input("Present or absent: ")

        print(attendance_tool(roll, subject, status))

    print("\nAsk Gemini a question.")
    question = input("Your question: ")

    print("\nAI Response:")
    print(ask_gemini(question))

else:
    print(student)