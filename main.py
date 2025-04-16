#main.py
import os
import threading
import random
import subprocess
from datetime import datetime
import time
import speech_recognition as sr
import wolframalpha
import re
from quit_module import quit_friday
from schedule_module import getSchedule
from teacher_schedule import get_teacher_schedule
from speech_module import takeCommand, speak, wake_word
from web_module import googleSearch, openYouTube, searchYouTube, openGoogle
from wikipedia_module import searchWikipedia
from holiday import show_holiday_calendar, push_notification
from talks import create_gui, run_meeting_summarizer
from mark_analysis import main_program
from plyer import notification
from attendence import main


# Initialize the recognizer
recognizer = sr.Recognizer()

# Global variable to handle sleep mode
sleep_mode = False

reminder_list = []  # To store scheduled reminders

def add_reminder():
    """Add a reminder."""
    speak("What time should I remind you? Please enter in HH:MM format using 24-hour clock.")
    reminder_time = input("Enter reminder time (HH:MM, 24-hour format): ").strip()
    speak("What should I remind you about?")
    reminder_task = input("Enter reminder task: ").strip()

    # Validate time input format
    try:
        reminder_hour, reminder_minute = map(int, reminder_time.split(":"))
        reminder_datetime = datetime.now().replace(
            hour=reminder_hour, minute=reminder_minute, second=0, microsecond=0
        )
        if reminder_datetime < datetime.now():
            speak("The specified time is in the past. Please enter a future time.")
            return

        # Add reminder to list
        reminder_list.append((reminder_datetime, reminder_task))
        speak(f"Reminder set for {reminder_time} to {reminder_task}.")
    except ValueError:
        speak("Invalid time format. Please try again using HH:MM in 24-hour format.")


# Reminder checker function to check the reminders in the background
def reminder_checker():
    """Continuously check reminders and notify when time matches."""
    while True:
        now = datetime.now()
        for reminder in reminder_list[:]:  # Copy the list to avoid modification issues
            reminder_time, reminder_task = reminder
            if now >= reminder_time:
                # Push notification and speak the reminder
                notification.notify(
                    title="Reminder Alert",
                    message=f"It's time to: {reminder_task}",
                    app_name="FRIDAY",
                    timeout=10,
                )
                speak(f"Sir, it's time to {reminder_task}.")
                # Remove the reminder from the list after notifying
                reminder_list.remove(reminder)
        # Small sleep to reduce CPU usage
        time.sleep(1)  # Use time.sleep(1) correctly here

# Start the reminder checker in a separate thread so it doesn't block the main program
reminder_thread = threading.Thread(target=reminder_checker, daemon=True)
reminder_thread.start()

todo_file = "To-Do.txt"  # This will store our to-do tasks

def load_tasks():
    """Load tasks from the file into the todo list."""
    if os.path.exists(todo_file):
        with open(todo_file, 'r') as file:
            return [line.strip() for line in file.readlines()]
    return []


def save_tasks(tasks):
    """Save the current tasks to the file."""
    with open(todo_file, 'w') as file:
        for task in tasks:
            file.write(f"{task}\n")


todo_list = load_tasks()  # Load tasks when the assistant starts


def wishMe():
    """Greet the user based on the time of day."""
    hour = int(datetime.now().hour)
    if hour < 12:
        speak(random.choice(
            [
                "Good morning. How may I assist you?",
                "Good morning."
            ]))
    elif hour < 18:
        speak(random.choice(
            [
               "Good afternoon. Everything is operating smoothly.",
               "A pleasant afternoon to you."
            ]))
    else:
        speak(random.choice(
            [
                "Good evening. How can I assist you tonight?",
                "A pleasant evening to you."
            ]))

    speak("I am Friday, your personal assistant. How may i help you?")


def add_task(task):
    """Add a task to the to-do list."""
    todo_list.append(task)
    save_tasks(todo_list)  # Save tasks to the file
    speak(f"Added to your to-do list: {task}")


def view_tasks():
    """View all tasks in the to-do list and show a notification."""
    if not todo_list:
        # Display the notification
        notification.notify(
            title="Today's Work",
            message="Your to-do list is empty.",
            app_name="FRIDAY",
            timeout=10
        )
        speak("Your to-do list is empty.")
    else:
        tasks = "\n".join([f"{i + 1}. {task}" for i, task in enumerate(todo_list)])
        # Display the notification
        notification.notify(
            title="Today's Work",
            message=tasks,
            app_name="FRIDAY",
            timeout=10  # Time in seconds for the notification to stay on screen
        )
        # Print and speak the tasks
        print("Here are your tasks:")
        print(tasks)
        speak("Here are your tasks:")
        speak(tasks)


def remove_task(task_number):
    """Remove a task from the to-do list by its number."""
    try:
        task_number = int(task_number) - 1  # Adjust for 0-based index
        if 0 <= task_number < len(todo_list):
            removed_task = todo_list.pop(task_number)
            save_tasks(todo_list)  # Save updated tasks to the file
            speak(f"Removed from your to-do list: {removed_task}")
            print(f"Removed from your to-do list: {removed_task}")
        else:
            speak("That task number does not exist.")
    except ValueError:
        speak("Please provide a valid task number.")


def randomRemarks():

    remarks = [
        "All systems functioning optimally, Sir.",
        "As always, at your service, Sir.",
        "Ready for your next directive, Sir.",
        "An excellent choice, as always, Sir.",
        "Everything seems in perfect working order. Shall we continue?",
        "A pleasure to serve, as always.",
        "Task complete. If you have further instructions, I'm at the ready.",
        "Flawlessly executed. Moving on to the next, Sir."
    ]
    speak(random.choice(remarks))



def takeCommandWithCheck():
    """Take command and ensure it is not empty."""
    while True:
        query = takeCommand().lower()
        if query == "none" or query.strip() == "":
            speak("I didn't catch that. Could you please repeat?")
            continue
        return query


# Function to handle sleep mode
def check_sleep_mode():
    global sleep_mode
    while sleep_mode:
        # Friday remains silent during sleep mode, only waiting for the wake-up word.
        query = takeCommand().lower()
        if 'wake up' in query:
            sleep_mode = False
            speak("I am back online and ready to help you.")
            break
        elif 'shutdown' in query:
            speak("Goodbye!")
            quit_friday()
            exit()


if __name__ == "__main__":
    print("Starting...")
    while True:
        speak("Waiting for activation.")
        # Wait for activation
        print("waiting...")

        if wake_word():
            speak("Welcome Sir.")
            wishMe()

            #Asking user's name
            speak("May I know your name?")
            user_name = takeCommandWithCheck()

            if user_name.lower() == "friday":
                speak("Hey, we have the same name! , Tell me what can i do for you")
            elif user_name.lower() == "no":
                speak("No problem, Tell me how may i help you")
            elif user_name.lower() != "friday quit":  # Prevent early exit
                speak(f"Hello {user_name}, what can I do for you today?")
            else:
                exit()

            # pushes notification of about today's event.
            push_notification()

                # Main interaction loop
            while True:
                if sleep_mode:
                    check_sleep_mode()
                    continue

                query = takeCommandWithCheck()  # Use the checked command input

                if "teacher schedule" in query or "teachers schedule" in query:
                    day_of_week = datetime.now().strftime("%A")
                    speak(f"Today is {day_of_week}.")
                    get_teacher_schedule()

                # Handling user commands
                elif 'schedule' in query:
                    day_of_week = datetime.now().strftime("%A")
                    speak(f"Today is {day_of_week}.")
                    todays_schedule = getSchedule(day_of_week)
                    speak(f"Here is your schedule for today, {user_name}:")
                    print(todays_schedule)
                    speak(todays_schedule)
                    randomRemarks()


                elif "hello friday" == query or "hi friday" == query or "hey friday" == query or "friday" == query:
                    speak("hello sir, How are you?")
                elif "fine" in query or "good" in query:
                    speak("that's great, sir")
                elif "how are you" in query or "how r u" in query:
                    speak("I am always perfect, sir")
                elif "thank" in query:
                    speak(random.choice(
                        ["You're very welcome.", "Anytime! I'm happy to help.","You're welcome; I'm glad i could assist."
                         "It was my pleasure!"]))


                elif "remind me" in query:
                    add_reminder()


                elif "check" in query or "social media" in query:
                    speak("sure sir")
                    speak("let me a moment to go through your social media profiles")
                    speak("you have 2 missed calls")
                    speak("4 unread messages on whatsApp")
                    speak("12 unread messages on instagram and 9 notifications")
                    speak("Additionaly you have 582 unread messages on telegram")
                    speak("Would you like me to reply anyone specifically?")
                    if "no" in query:
                        pass
                    else:
                        "speak getting some error right now, sorry i can't reply"


                elif "mark analysis" in query:
                    speak("launching Sir.")
                    main_program()
                    randomRemarks()


                elif "attendence" in query or "register" in query or "present" in query:
                    speak("launching attendence register")
                    main()
                    randomRemarks()


                # New holiday command
                elif 'holiday calendar' in query or 'show holidays' in query:
                    speak("Opening the holiday calendar now.")
                    show_holiday_calendar()  # Call the function to show the holiday calendar
                    randomRemarks()


                elif "start meeting summarizer" in query or "summarize meeting" in query or "meeting" == query:
                    speak("Launching the meeting summarizer.")
                    create_gui()  # Opens the GUI for the user


                # Adding tasks
                elif "add to do" in query:
                    task = query.replace("add to do", "").strip()
                    if task:
                        add_task(task)
                    else:
                        speak("What task would you like to add?")

                # Viewing tasks
                elif "show my task" == query:
                    view_tasks()

                # Removing tasks
                elif "remove task" in query:
                    view_tasks()  # Show tasks before removal
                    speak("Which task number would you like to remove?")
                    task_number = input("Please enter the task number to remove: ")
                    remove_task(task_number)


                elif "focus mode" in query:
                    a = int(input("Are you sure, that you want to enter focus mode :- [1 for Yes / 2 for No]: "))
                    if a == 1:
                        speak("Entering the focus mode")
                        subprocess.Popen(["python", r"C:\Users\ak790\OneDrive\Desktop\PythonProject\Focus_Mode.py"], shell=True)
                        #exit()
                    else:
                        pass


                elif 'open google' in query:
                    openGoogle()
                    randomRemarks()


                elif 'open youtube' in query:
                    openYouTube()
                    randomRemarks()


                elif "open" in query:
                    from Dictapp import openappweb
                    openappweb(query)
                elif "close" in query:
                    from Dictapp import closeappweb
                    closeappweb(query)



                elif "remember that" in query:
                    # Extract the message to remember
                    rememberMessage = query.replace("remember that", "").strip()
                    rememberMessage = rememberMessage.replace("friday", "").strip()
                    speak(f"You told me to remember: {rememberMessage}")
                    # Overwrite the file with the new memory
                    with open("remember.txt", "w") as remember_file:
                        remember_file.write(rememberMessage)

                elif "what do you remember" in query:
                    # Read the last remembered message
                    try:
                        with open("remember.txt", "r") as remember_file:
                            remembered_message = remember_file.read().strip()
                            if remembered_message:
                                speak(f"You told me to remember: {remembered_message}")
                                print(f"You told me to remember: {remembered_message}")
                            else:
                                speak("I don't have anything to remember.")
                    except FileNotFoundError:
                        speak("I don't have anything to remember.")



                elif 'wikipedia' in query:
                    speak('Allow me to look that up for you...')
                    query = query.replace("wikipedia", "").strip()
                    result = searchWikipedia(query)
                    speak("According to Wikipedia")
                    print(result)
                    speak(result)
                    randomRemarks()


                elif 'transcript' in query or 'summarize' in query:
                    from transcript import handle_video_transcript
                    handle_video_transcript()
                    randomRemarks()


                elif 'search on youtube' in query:
                    speak("What would you like to search on youtube...")
                    search_query = takeCommandWithCheck()
                    speak(f"Opening {search_query} on YouTube...")
                    searchYouTube(search_query)

                elif 'youtube' in query:
                    search_query = query.replace("youtube", "").strip()  # Remove "YouTube" from the query
                    if search_query:  # If there's a search term present
                        speak(f"Opening {search_query} YouTube...")
                        searchYouTube(search_query)  # Perform the search directly
                    else:
                        speak("What would you like to search for on YouTube?")
                        search_query = takeCommandWithCheck()  # Listen for user's input
                        speak(f"Opening {search_query} YouTube...")
                        searchYouTube(search_query)  # Perform the search with user's input


                elif 'search on google' in query:
                    speak("What would you like to search for on Google?")
                    search_query = takeCommandWithCheck()
                    speak(f"Searching Google for {search_query}...")
                    googleSearch(search_query)

                elif 'google' in query:
                    search_query = query.replace("google", "").strip()  # Remove "google" from the query
                    if search_query:  # If there's a search term present
                        speak(f"Searching Google for {search_query}...")
                        googleSearch(search_query)  # Perform the direct search
                    else:
                        speak("What would you like to search for on Google?")
                        search_query = takeCommandWithCheck()  # Listen for user's input
                        googleSearch(search_query)  # Perform the search with user's input


                elif 'time' in query:
                    strTime = datetime.now().strftime("%H:%M:%S")
                    speak(f"The time is {strTime}, Sir.")
                    randomRemarks()


                elif "weather" in query:
                    from weather import weather_forecast
                    weather_forecast()


                elif "news" in query:
                    from News_Read import latest_news
                    latest_news()

                # WolframAlpha Enhanced Question Handling
                elif any(x in query for x in ["calculate", "what is", "who", "which", "how ", "why"]):
                    app_id = "W57TAA-6RKYTHRYP5"
                    client = wolframalpha.Client(app_id)
                    try:
                        # Identify the question keyword
                        match = re.search(r"(what|who|which|how|why)\s+is\s+(.*)", query, re.IGNORECASE)
                        if match:
                            question_content = match.group(2)  # Extracts the main query content
                        else:
                            question_content = query.replace("calculate", "").strip()  # Handle "calculate" separately

                        # Query WolframAlpha
                        result = client.query(question_content)
                        ans = next(result.results).text
                        speak("The answer is " + ans)
                        print("The answer is " + ans)

                    except (StopIteration, AttributeError):
                        speak("I'm sorry, I couldn't find an answer for that. Please try rephrasing.")
                        print("I'm sorry, I couldn't find an answer for that.")


                # Sleep mode
                elif 'go to sleep' in query:
                    speak("I am going to sleep. Say 'wake up' when you need me.")
                    sleep_mode = True


                elif query == "friday quit":
                    print("Goodbye, Sir!")
                    speak("Goodbye, Sir.")
                    quit_friday()
                    exit()

                else:
                    speak("Apologies, I didn't understand that.")
