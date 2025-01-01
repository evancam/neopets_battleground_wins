import csv
import datetime
import os
import requests
import sys
import time
from bs4 import BeautifulSoup

from constants import BATTLEGROUND_CHALLENGERS

def fetch_total_wins(username):
    """
    Fetches the total wins for specified challengers for a given username.
    Args:
        username (str): The Neopets username.
    Returns:
        int: Total wins for specified challengers.
    """
    base_url = "https://www.neopets.com/dome/record.phtml?username="
    url = base_url + username

    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        total_wins = 0

        table = soup.find("table", class_="recordsTable")
        if table:
            rows = table.find_all("tr", class_="recordRow")
            for row in rows:
                name_cell = row.find("td", class_="name")
                wins_cell = row.find("td", class_="won")

                if name_cell and wins_cell:
                    challenger_name = name_cell.get_text(strip=True)
                    wins = int(wins_cell["data-won"])

                    if challenger_name in BATTLEGROUND_CHALLENGERS:
                        total_wins += wins

        return total_wins
    else:
        print(f"Failed to fetch data for {username}. HTTP Status Code: {response.status_code}")
        return 0


def load_weekly_data(input_csv_path, valid_users):
    """
    Load existing weekly data from the input CSV.
    Args:
        input_csv_path (str): Path to the input CSV file.
        valid_users (set): Set of valid usernames.
    Returns:
        dict: Weekly data for valid users.
    """
    weekly_data = {}
    if os.path.exists(input_csv_path):
        with open(input_csv_path, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                username = row[""]
                if username in valid_users:
                    weekly_data[username] = row
    return weekly_data


def process_user(username, weekly_data, current_week):
    """
    Fetch and process total wins for a single user.
    Args:
        username (str): The username to process.
        weekly_data (dict): The current weekly data.
        current_week (str): The current week's date.
    Returns:
        dict: Updated weekly data for the user.
    """
    total_wins = fetch_total_wins(username)
    print(f"Processing {username}")

    if username not in weekly_data:
        weekly_data[username] = {"": username}

    weekly_data[username][current_week] = total_wins

    # Get the most recent week before the current week
    weeks = sorted(
        [week for week in weekly_data[username] if week not in ["", "# wins this week", "Last battled week"]]
    )
    last_week = weeks[-2] if len(weeks) > 1 else None

    # Calculate the number of wins this week
    wins_this_week = total_wins - int(weekly_data[username].get(last_week, 0)) if last_week else total_wins
    weekly_data[username]["# wins this week"] = wins_this_week

    # Determine the last battled week
    weekly_data[username]["Last battled week"] = determine_last_battled_week(weekly_data[username], total_wins)

    return weekly_data


def determine_last_battled_week(user_data, total_wins):
    """
    Determine the last battled week for a user.
    Args:
        user_data (dict): Weekly data for the user.
    Returns:
        str: The date of the last battled week.
    """
    weeks = sorted(
        [week for week in user_data if week not in ["", "# wins this week", "Last battled week"]]
    )
    last_battled_week = None
    for i in range(len(weeks) - 1, -1, -1):  # Iterate from the most recent to oldest
        current_week = weeks[i]
        if not user_data[current_week]: 
            last_battled_week = weeks[i+1] 
            break
        elif (total_wins - int(user_data[current_week])) > 0:
            last_battled_week = current_week
            break
        
    return last_battled_week


def write_output_csv(output_csv_path, weekly_data):
    """
    Write the updated weekly data to the output CSV.
    Args:
        output_csv_path (str): Path to the output CSV file.
        weekly_data (dict): The updated weekly data.
    """
    all_weeks = sorted(
        {week for data in weekly_data.values() for week in data if week not in ["", "# wins this week", "Last battled week"]}
    )
    headers = [""] + all_weeks + ["# wins this week", "Last battled week"]

    with open(output_csv_path, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        for user_data in weekly_data.values():
            writer.writerow(user_data)


def update_or_create_csv(input_csv_path, output_csv_path, usernames):
    """
    Updates an existing CSV with the current week's data or creates a new file.
    Args:
        input_csv_path (str): Path to the input CSV file.
        output_csv_path (str): Path to the output CSV file.
        usernames (list): List of usernames to process.
    """
    current_week = str((datetime.date.today() - datetime.timedelta(days=datetime.date.today().weekday())).isoformat())
    valid_users = set(usernames)

    # Load existing data
    weekly_data = load_weekly_data(input_csv_path, valid_users)

    # Process each user
    for username in usernames:
        weekly_data = process_user(username, weekly_data, current_week)
        time.sleep(60)  # Crawl delay

    # Write updated data to the output CSV
    write_output_csv(output_csv_path, weekly_data)


def main(usernames_csv_path, input_csv_path="default.csv", output_csv_path="default.csv"):
    """
    Main function to update or create a weekly wins CSV.
    Args:
        usernames_csv_path (str): Path to the CSV containing usernames.
        input_csv_path (str): Path to the existing CSV with weekly data (default is `default.csv`).
        output_csv_path (str): Path to save the updated CSV (default is `default.csv`).
    """
    # Load usernames from CSV
    with open(usernames_csv_path, "r") as file:
        usernames = [row[0] for row in csv.reader(file)]

    update_or_create_csv(input_csv_path, output_csv_path, usernames)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <usernames_csv_path> [<input_csv_path>] [<output_csv_path>]")
    else:
        usernames_csv_path = sys.argv[1]
        input_csv_path = sys.argv[2] if len(sys.argv) > 2 else "default.csv"
        output_csv_path = sys.argv[3] if len(sys.argv) > 3 else "default.csv"
        main(usernames_csv_path, input_csv_path, output_csv_path)