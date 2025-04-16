import tkinter as tk
from tkinter import messagebox, simpledialog
import calendar
import json
from datetime import datetime, timedelta
import os
from plyer import notification  # For notifications

# File to save events
EVENTS_FILE = "saved_events.json"

# List of holidays with optional durations
holidays = [
    {"name": "New Year's Day", "date": "01-01-2024"},
    {"name": "Makar Sankranti", "date": "15-01-2024"},
    {"name": "Republic Day", "date": "26-01-2024"},
    {"name": "Basant Panchami / Saraswati Puja", "date": "14-02-2024"},
    {"name": "Maha Shivaratri", "date": "08-03-2024"},
    {"name": "Shab-e-Barat", "date": "25-03-2024"},
    {"name": "Holi", "date": "24-03-2024", "duration": 2},  # Duration of 2 days for Holi
    {"name": "Good Friday", "date": "29-03-2024"},
    {"name": "Ram Navami", "date": "17-04-2024"},
    {"name": "Mahavir Jayanti", "date": "21-04-2024"},
    {"name": "Eid-ul-Fitr", "date": "10-04-2024", "duration": 2},  # 2 days for Eid-ul-Fitr
    {"name": "Buddha Purnima", "date": "23-05-2024"},
    {"name": "Eid al-Adha", "date": "16-06-2024", "duration": 2},  # 2 days for Eid al-Adha
    {"name": "Independence Day", "date": "15-08-2024"},
    {"name": "Raksha Bandhan", "date": "19-08-2024"},
    {"name": "Janmashtami", "date": "26-08-2024"},
    {"name": "Ganesh Chaturthi", "date": "07-09-2024", "duration": 10},  # 10 days for Ganesh Chaturthi
    {"name": "Onam", "date": "20-08-2024", "duration": 10},  # 10 days for Onam
    {"name": "Gandhi Jayanti", "date": "02-10-2024"},
    {"name": "Navratri", "date": "03-10-2024", "duration": 9},  # 9 days for Navratri
    {"name": "Dussehra", "date": "12-10-2024"},
    {"name": "Karva Chauth", "date": "20-10-2024"},
    {"name": "Diwali chhath puja", "date": "31-10-2024", "duration": 10},  # 10 days for Diwali
    {"name": "Guru Nanak Jayanti", "date": "15-11-2024"},
    {"name": "Christmas", "date": "25-12-2024", "duration": 6}
]

# List to store custom events (loaded from JSON)
custom_events = []


def load_events():
    """Load custom events from the JSON file."""
    global custom_events
    if os.path.exists(EVENTS_FILE):
        with open(EVENTS_FILE, "r") as file:
            custom_events = json.load(file)
    else:
        custom_events = []


def save_events():
    """Save custom events to the JSON file."""
    with open(EVENTS_FILE, "w") as file:
        json.dump(custom_events, file, indent=4)


def get_event_for_date(day, month, year):
    """Check if there is a custom event or holiday on a given date."""
    # Check custom events first
    for event in custom_events:
        if event["day"] == day and event["month"] == month and event["year"] == year:
            return f"Custom Event: {event['name']}"

    # Check predefined holidays
    for holiday in holidays:
        holiday_date = datetime.strptime(holiday["date"], "%d-%m-%Y")

        # If the holiday spans multiple days, check if the day is within the range
        if "duration" in holiday:
            start_date = holiday_date
            end_date = start_date + timedelta(days=holiday["duration"] - 1)
            if start_date <= datetime(year, month, day) <= end_date:
                return f"Holiday: {holiday['name']}"
        else:
            if holiday_date.day == day and holiday_date.month == month and holiday_date.year == year:
                return f"Holiday: {holiday['name']}"

    return None


def show_event_info(day, month, year, is_sunday=False):
    """Display event or holiday info on click."""
    if is_sunday:
        messagebox.showinfo("Sunday Holiday", f"Sunday Holiday on {day:02d}-{month:02d}-{year}")
    else:
        event = get_event_for_date(day, month, year)
        if event:
            messagebox.showinfo("Event Info", f"{event} on {day:02d}-{month:02d}-{year}")
        else:
            messagebox.showinfo("No Event", f"No event on {day:02d}-{month:02d}-{year}")


def save_event(root, month, year):
    """Save a custom event."""
    date_input = simpledialog.askstring("Save Event", "Enter the date (dd-mm-yyyy):")
    if not date_input:
        return
    try:
        event_date = datetime.strptime(date_input, "%d-%m-%Y")
    except ValueError:
        messagebox.showerror("Invalid Date", "Please enter a valid date in the format dd-mm-yyyy.")
        return

    event_name = simpledialog.askstring("Save Event", "Enter the event name:")
    if not event_name:
        return

    # Add the event to the custom events list
    custom_events.append({
        "day": event_date.day,
        "month": event_date.month,
        "year": event_date.year,
        "name": event_name
    })
    save_events()  # Save events to file
    messagebox.showinfo("Event Saved", f"Event '{event_name}' saved on {event_date.strftime('%d-%m-%Y')}.")

    # Refresh the calendar to reflect the new event
    create_calendar(root, month, year)


def create_calendar(root, month, year):
    """Create a calendar GUI with clickable dates."""
    # Clear existing widgets
    for widget in root.winfo_children():
        widget.destroy()

    # Display the month and year
    month_name = calendar.month_name[month]
    header = tk.Label(root, text=f"{month_name} {year}", font=("Arial", 16))
    header.grid(row=0, column=1, columnspan=5)

    # Add navigation buttons
    prev_button = tk.Button(root, text="<", command=lambda: navigate_calendar(root, month - 1, year))
    prev_button.grid(row=0, column=0, padx=5, pady=5)
    next_button = tk.Button(root, text=">", command=lambda: navigate_calendar(root, month + 1, year))
    next_button.grid(row=0, column=6, padx=5, pady=5)

    # Add button to save events
    save_event_button = tk.Button(root, text="Save Event", command=lambda: save_event(root, month, year))
    save_event_button.grid(row=0, column=5, padx=5, pady=5)

    # Add the days of the week headers
    days_of_week = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
    for i, day in enumerate(days_of_week):
        day_label = tk.Label(root, text=day, font=("Arial", 12))
        day_label.grid(row=1, column=i, padx=10, pady=5)

    # Get the month calendar
    month_calendar = calendar.monthcalendar(year, month)

    # Create buttons for each day
    for row, week in enumerate(month_calendar):
        for col, day in enumerate(week):
            if day != 0:  # Skip empty days
                is_sunday = (col == 6)
                day_button = tk.Button(
                    root, text=str(day), width=5, height=2,
                    command=lambda day=day, is_sunday=is_sunday: show_event_info(day, month, year, is_sunday)
                )
                # Highlight Sundays in gray
                if is_sunday:
                    day_button.config(bg="gray")
                # Highlight custom events in blue
                for event in custom_events:
                    if event["day"] == day and event["month"] == month and event["year"] == year:
                        day_button.config(bg="blue")
                        break
                # Highlight holidays in green
                if not day_button.cget("bg") == "blue":  # Avoid overwriting custom events
                    event = get_event_for_date(day, month, year)
                    if event and "Holiday" in event:
                        day_button.config(bg="green")
                day_button.grid(row=row + 2, column=col, padx=10, pady=10)


def navigate_calendar(root, month, year):
    """Handle month navigation."""
    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1
    create_calendar(root, month, year)


def push_notification():
    """Send a push notification for today's event."""
    today = datetime.now()
    event = get_event_for_date(today.day, today.month, today.year)
    if event:
        notification.notify(
            title="Today's Event",
            message=event,
            timeout=5
        )
    else:
        notification.notify(
            title="No Event Today",
            message="There are no events today.",
            timeout=5
        )


def show_holiday_calendar():
    """Create and show the holiday calendar GUI."""
    # Load saved events
    load_events()

    root = tk.Tk()
    root.title("Holiday Calendar")

    now = datetime.now()
    current_year = now.year
    current_month = now.month

    create_calendar(root, current_month, current_year)
    root.mainloop()
