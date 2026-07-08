import requests
import os
import re
from bs4 import BeautifulSoup

URL = "https://www.bamf.de/DE/Themen/Integration/ZugewanderteTeilnehmende/Einbuergerung/einbuergerung-node.html"
STATUS_FILE = "bamf_status.txt"
CHANGES_FILE = "changes.txt"

def get_bamf_status():
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(URL, headers=headers)
    response.raise_for_status()
    
    # Parse the page and extract all text
    soup = BeautifulSoup(response.text, 'html.parser')
    text_content = soup.get_text(separator=" ")

    # Regex to find the specific sentence. 
    # .*? allows it to flexibly grab the date even if there are extra spaces.
    pattern = r"Aktuell wertet das Bundesamt Tests bis Prüfungsdatum.*?aus\."
    match = re.search(pattern, text_content, re.IGNORECASE)

    if match:
        # Clean up any weird spacing issues
        return " ".join(match.group(0).split())
    else:
        raise ValueError("Target sentence not found. BAMF might have changed the website layout or wording.")

if __name__ == "__main__":
    try:
        current_status = get_bamf_status()
        print(f"Current status found: {current_status}")

        old_status = ""
        if os.path.exists(STATUS_FILE):
            with open(STATUS_FILE, "r", encoding="utf-8") as f:
                old_status = f.read().strip()

        # If the status is different, log it and prepare for GitHub Actions to catch it
        if current_status != old_status:
            print(f"Change detected: '{old_status}' -> '{current_status}'")
            
            # Save the new state
            with open(STATUS_FILE, "w", encoding="utf-8") as f:
                f.write(current_status)
            
            # Write the notification payload
            with open(CHANGES_FILE, "w", encoding="utf-8") as f:
                if old_status:
                    f.write(f"**BAMF Test Evaluation Date Changed!**\n\n**Old:** {old_status}\n**New:** {current_status}\n\n[Check the BAMF Website]({URL})")
                else:
                    f.write(f"**Initial BAMF Test Evaluation Date Recorded:**\n\n{current_status}\n\n[Check the BAMF Website]({URL})")
        else:
            print("No changes detected today.")

    except Exception as e:
        print(f"Script failed: {e}")
        # Write the error to changes.txt so you get an issue if the crawler breaks
        with open(CHANGES_FILE, "w", encoding="utf-8") as f:
            f.write(f"**BAMF Crawler Error:**\n\nThe script failed with the following error:\n`{e}`\n\nPlease check if the [BAMF website]({URL}) is down or if the text format changed.")
        exit(1)
