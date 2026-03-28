# SI 201 HW4 (Library Checkout System)
# Your name: wale alawiye
# Your student id: 07549839
# Your email: alawiye@umich.edu
# Who or what you worked with on this homework (including generative AI like ChatGPT): Asked Claude for debugging help
# If you worked with generative AI also add a statement for how you used it.
# e.g.:
# Asked ChatGPT for hints on debugging and for suggestions on overall code structure
#
# Did your use of GenAI on this assignment align with your goals and guidelines in your Gen AI contract? If not, why?
# Yes
# --- ARGUMENTS & EXPECTED RETURN VALUES PROVIDED --- #
# --- SEE INSTRUCTIONS FOR FULL DETAILS ON METHOD IMPLEMENTATION --- #

from bs4 import BeautifulSoup
import re
import os
import csv
import unittest
import requests  # kept for extra credit parity


# IMPORTANT NOTE:
"""
If you are getting "encoding errors" while trying to open, read, or write from a file, add the following argument to any of your open() functions:
    encoding="utf-8-sig"
"""


def load_listing_results(html_path) -> list[tuple]:
    """
    Load file data from html_path and parse through it to find listing titles and listing ids.

    Args:
        html_path (str): The path to the HTML file containing the search results

    Returns:
        list[tuple]: A list of tuples containing (listing_title, listing_id)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    from bs4 import BeautifulSoup

    html_path = os.path.join(os.path.dirname(__file__), "html_files", "search_results.html")
    with open(html_path, encoding="utf-8-sig") as f:
        soup = BeautifulSoup(f, "html.parser")
    
    listings = []

    title_divs = soup.find_all("div", {"data-testid": "listing-card-title"})

    for div in title_divs:
        title = div.get_text().strip()
        # Gets the id attribute and removes the title_ to isolate the actual listing ID
        listing_id = div.get("id").replace("title_", "")
        # Adds the (title, listing_id) tuple to results list
        listings.append((title, listing_id))

    return listings
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def get_listing_details(listing_id) -> dict:
    """
    Parse through listing_<id>.html to extract listing details.

    Args:
        listing_id (str): The listing id of the Airbnb listing

    Returns:
        dict: Nested dictionary in the format:
        {
            "<listing_id>": {
                "policy_number": str,
                "host_type": str,
                "host_name": str,
                "room_type": str,
                "location_rating": float
            }
        }
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    
    filename = os.path.join(os.path.dirname(__file__), "html_files", f"listing_{listing_id}.html")
    with open(filename, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # POLICY NUMBER 
    policy_number = ""
    policy_section = soup.find(string=re.compile(r"Policy number", re.I))
    if policy_section:
        parent = policy_section.parent  # the <li>
        span = parent.find("span")
        if span:
            text = span.get_text().strip()
            if "pending" in text:
                policy_number = "Pending"
            elif "exempt" in text:
                policy_number = "Exempt"
            else:
                policy_number = text

    # ROOM TYPE, HOST NAME 
    room_type = "Entire Room"
    host_name = ""

    subtitle = soup.find("h2", {"elementtiming": "LCP-target"})
    if subtitle:
        text = subtitle.get_text().strip()
        # room type
        if "Private" in text:
            room_type = "Private Room"
        elif "Shared" in text:
            room_type = "Shared Room"
        if "hosted by" in text.lower():
            host_name = text.split("hosted by")[-1].strip()
            host_name = host_name.replace("\xa0", "").strip()

    # HOST TYPE
    host_type = "regular"
    superhost_tag = soup.find(string=re.compile(r"is a Superhost", re.I))
    if superhost_tag:
        host_type = "Superhost"

    # LOCATION RATING
    location_rating = 0.0
    loc_label = soup.find("div", class_="_y1ba89", string="Location")
    if loc_label:
        rating_div = loc_label.find_next_sibling("div")
        if rating_div:
            inner = rating_div.find("div", {"aria-label": re.compile(r"out of 5")})
            if inner:
                match = re.search(r"([0-9.]+)", inner["aria-label"])
                if match:
                    location_rating = float(match.group(1))

    #  COMBINE 
    details = {
        listing_id: {
            "policy_number": policy_number,
            "host_type": host_type,
            "host_name": host_name,
            "room_type": room_type,
            "location_rating": location_rating
        }
    }

    return details
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def create_listing_database(html_path) -> list[tuple]:
    """
    Use prior functions to gather all necessary information and create a database of listings.

    Args:
        html_path (str): The path to the HTML file containing the search results

    Returns:
        list[tuple]: A list of tuples. Each tuple contains:
        (listing_title, listing_id, policy_number, host_type, host_name, room_type, location_rating)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================

    # Calls load_listing_results to get a list of title,listing_id tuples
    listings_basic = load_listing_results(html_path)

    # Empty list
    database = []

    # Loops through each listing found in the search results
    for title, listing_id in listings_basic:
        # Calls get_listing_details to parse the individual listing HTML and return a dictionary of the details
        details_dict = get_listing_details(listing_id)
        # Uses .get() to extract the dictionary for the current listing_id
        details = details_dict.get(listing_id, {})


        # Pulls out all required fields and provides default values if anything is missing
        policy_number = details.get("policy_number", "")
        host_type = details.get("host_type", "")
        host_name = details.get("host_name", "")
        room_type = details.get("room_type", "")
        location_rating = details.get("location_rating", 0.0)

        # Makes one tuple with all listing data
        listing_tuple = (
            title,
            listing_id,
            policy_number,
            host_type,
            host_name,
            room_type,
            location_rating,
        )

        # Appends the tuple to the database list
        database.append(listing_tuple)

    return database

    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def output_csv(data, filename) -> None:
    """
    Write data to a CSV file with the provided filename.

    Sort by Location Rating (descending).

    Args:
        data (list[tuple]): A list of tuples containing listing information
        filename (str): The name of the CSV file to be created and saved to

    Returns:
        None
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    
    # Sort data by location_rating in descending order
    data_sorted = sorted(data, key=lambda x: x[6], reverse=True)

    # Opens the file for writing
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # Writes header
        writer.writerow(["Listing Title", "Listing ID", "Policy Number", "Host Type", "Host Name", "Room Type", "Location Rating"])
        # Writes data rows
        for row in data_sorted:
            writer.writerow(row)

    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def avg_location_rating_by_room_type(data) -> dict:
    """
    Calculate the average location_rating for each room_type.

    Excludes rows where location_rating == 0.0 (meaning the rating
    could not be found in the HTML).

    Args:
        data (list[tuple]): The list returned by create_listing_database()

    Returns:
        dict: {room_type: average_location_rating}
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    
    # Empty dictionary to store lists of ratings per room type
    ratings = {}
    
    # Loops through each listing tuple in data
    for entry in data:
        room_type = entry[5]  # room_type is at index 5
        location_rating = entry[6]  # location_rating is at index 6
        
        if location_rating == 0.0:
            continue  # skips missing ratings
        
        if room_type not in ratings:
            ratings[room_type] = [] # Empty list for room_type that is not in ratings
        
        # Append the rating to the 
        ratings[room_type].append(location_rating)
    
    # Compute average
    avg_ratings = {room: sum(vals)/len(vals) for room, vals in ratings.items()}
    return avg_ratings

    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def validate_policy_numbers(data) -> list[str]:
    """
    Validate policy_number format for each listing in data.
    Ignore "Pending" and "Exempt" listings.

    Args:
        data (list[tuple]): A list of tuples returned by create_listing_database()

    Returns:
        list[str]: A list of listing_id values whose policy numbers do NOT match the valid format
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    
    invalid_ids = []

    # Loop through each listing tuple in data
    for entry in data:
        listing_id = entry[1]   # listing_id is at index 1
        policy_number = entry[2] # policy_number is at index 2

        # Skip Pending or Exempt
        if policy_number.lower() in ["pending", "exempt"]:
            continue

        # Checks for valid format which is STR-000#### or 20##-00####STR
        if not re.match(r"^(STR-\d{7}|20\d{2}-\d{6}STR)$", policy_number):
            invalid_ids.append(listing_id)

    return invalid_ids

    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


# EXTRA CREDIT
def google_scholar_searcher(query):
    """
    EXTRA CREDIT

    Args:
        query (str): The search query to be used on Google Scholar
    Returns:
        List of titles on the first page (list)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    import requests
    from bs4 import BeautifulSoup

    url = f"https://scholar.google.com/scholar?q={query}"
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    titles = []
    for tag in soup.find_all("h3", class_="gs_rt"):
        titles.append(tag.get_text())
    
    return titles
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


class TestCases(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.abspath(os.path.dirname(__file__))
        self.search_results_path = os.path.join(self.base_dir, "html_files", "search_results.html")

        self.listings = load_listing_results(self.search_results_path)
        self.detailed_data = create_listing_database(self.search_results_path)

    def test_load_listing_results(self):
        # TODO: Check that the number of listings extracted is 18.
        # TODO: Check that the FIRST (title, id) tuple is  ("Loft in Mission District", "1944564").
        
        # Check total listings
        self.assertEqual(len(self.listings), 18)
        # Check first listing tuple
        self.assertEqual(self.listings[0], ("Loft in Mission District", "1944564"))

    def test_get_listing_details(self):
        html_list = ["467507", "1550913", "1944564", "4614763", "6092596"]

        # TODO: Call get_listing_details() on each listing id above and save results in a list.

        # TODO: Spot-check a few known values by opening the corresponding listing_<id>.html files.
        # 1) Check that listing 467507 has the correct policy number "STR-0005349".
        # 2) Check that listing 1944564 has the correct host type "Superhost" and room type "Entire Room".
        # 3) Check that listing 1944564 has the correct location rating 4.9.
        
        listing_ids = ["467507", "1550913", "1944564", "4614763", "6092596"]
        # Call get_listing_details on each id
        results = [get_listing_details(listingid) for listingid in listing_ids]
         # Spot-check values
        self.assertEqual(results[0]["467507"]["policy_number"], "STR-0005349")
        self.assertEqual(results[2]["1944564"]["host_type"], "Superhost")
        self.assertEqual(results[2]["1944564"]["room_type"], "Entire Room")
        self.assertAlmostEqual(results[2]["1944564"]["location_rating"], 4.9)

    def test_create_listing_database(self):
        # TODO: Check that each tuple in detailed_data has exactly 7 elements:
        # (listing_title, listing_id, policy_number, host_type, host_name, room_type, location_rating)

        # Check that each tuple has 7 elements
        for tup in self.detailed_data:
            self.assertEqual(len(tup), 7)
        # Spot check last tuple
        self.assertEqual(
            self.detailed_data[-1],
            ("Guest suite in Mission District", "467507", "STR-0005349", "Superhost", "Jennifer", "Entire Room", 4.8)
        )


    def test_output_csv(self):
        out_path = os.path.join(self.base_dir, "test.csv")

        # TODO: Call output_csv() to write the detailed_data to a CSV file.
        # TODO: Read the CSV back in and store rows in a list.
        # TODO: Check that the first data row matches ["Guesthouse in San Francisco", "49591060", "STR-0000253", "Superhost", "Ingrid", "Entire Room", "5.0"].

        output_csv(self.detailed_data, out_path)
        # Read CSV back
        with open(out_path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)
        # Check first data row (skip header if your output_csv writes headers)
        first_row = rows[1] if rows[0][0] == "Listing Title" else rows[0]
        self.assertEqual(
            first_row,
            ["Guesthouse in San Francisco", "49591060", "STR-0000253", "Superhost", "Ingrid", "Entire Room", "5.0"]
        )

        os.remove(out_path)

    def test_avg_location_rating_by_room_type(self):
        # TODO: Call avg_location_rating_by_room_type() and save the output.
        # TODO: Check that the average for "Private Room" is 4.9.

        avg_ratings = avg_location_rating_by_room_type(self.detailed_data)
        self.assertAlmostEqual(avg_ratings.get("Private Room", 0), 4.9)

    def test_validate_policy_numbers(self):
        # TODO: Call validate_policy_numbers() on detailed_data and save the result into a variable invalid_listings.
        # TODO: Check that the list contains exactly "16204265" for this dataset.
        
        invalid_listings = validate_policy_numbers(self.detailed_data)
        self.assertEqual(invalid_listings, ["16204265"])



def main():
    detailed_data = create_listing_database(os.path.join("html_files", "search_results.html"))
    output_csv(detailed_data, "airbnb_dataset.csv")

if __name__ == "__main__":
    main()
    unittest.main(verbosity=2)

