import csv
import os
import requests
from bs4 import BeautifulSoup
import time
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

def update_or_create_csv(input_csv_path, output_csv_path, usernames):
    """
    Updates an existing CSV with the current week's data or creates a new file.

    Args:
        input_csv_path (str): Path to the input CSV file.
        output_csv_path (str): Path to the output CSV file.
        usernames (list): List of usernames to process.
    """
    weekly_data = {}
    current_week = "2024-12-01"  # Replace with dynamic date logic if needed

    if os.path.exists(input_csv_path):
        with open(input_csv_path, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                username = row[""]
                weekly_data[username] = row

    # Process each username
    for username in usernames:
        total_wins = fetch_total_wins(username)
        time.sleep(60)  # Crawl delay

        if username not in weekly_data:
            weekly_data[username] = {"": username}

        weekly_data[username][current_week] = total_wins

        # Calculate the number of wins this week
        last_two_weeks = sorted([week for week in weekly_data[username] if week != "" and week != "# wins this week" and week != "Last battled week"], reverse=True)[:2]
        wins_this_week = total_wins - int(weekly_data[username].get(last_two_weeks[1], 0)) if len(last_two_weeks) > 1 else total_wins
        weekly_data[username]["# wins this week"] = wins_this_week
        weekly_data[username]["Last battled week"] = current_week if total_wins > 0 else weekly_data[username].get("Last battled week", current_week)

    # Write updated data to the output CSV
    all_weeks = sorted(
        {week for data in weekly_data.values() for week in data if week != "" and week != "# wins this week" and week != "Last battled week"}
    )
    headers = [""] + all_weeks + ["# wins this week", "Last battled week"]

    with open(output_csv_path, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        for user_data in weekly_data.values():
            writer.writerow(user_data)

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
        print("Usage: python script.py <usernames_csv_path> [<input_csv_path>] [<output_csv_path>]")
    else:
        usernames_csv_path = sys.argv[1]
        input_csv_path = sys.argv[2] if len(sys.argv) > 2 else "default.csv"
        output_csv_path = sys.argv[3] if len(sys.argv) > 3 else "default.csv"
        main(usernames_csv_path, input_csv_path, output_csv_path)