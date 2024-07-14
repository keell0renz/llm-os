
import os
import socket
import psutil
import datetime

def get_os_uname_a() -> str:
    """
    Returns the system's uname information as a string.
    """
    uname = os.uname()
    return f"{uname.sysname} {uname.nodename} {uname.release} {uname.version} {uname.machine}"

def get_date() -> str:
    """
    Returns the current date as a string in the format YYYY-MM-DD.
    """
    return datetime.datetime.now().strftime("%Y-%m-%d")

def get_time() -> str:
    """
    Returns the current time as a string in the format HH:MM:SS.
    """
    return datetime.datetime.now().strftime("%H:%M:%S")

def get_timezone() -> str:
    """
    Returns the current timezone as a string.
    """
    return str(datetime.datetime.now(datetime.timezone.utc).astimezone().tzname())

def get_country() -> str:
    """
    Returns the country of the user as a string.
    Extracts from the environment variable USERS_COUNTRY.
    """
    return os.getenv("USERS_COUNTRY", "Unknown")

def get_city() -> str:
    """
    Returns the city of the user as a string.
    Extracts from the environment variable USERS_CITY.
    """
    return os.getenv("USERS_CITY", "Unknown")

def get_username() -> str:
    """
    Returns the username of the current user as a string.
    """
    return os.getlogin()

def get_users_real_name() -> str:
    """
    Returns the real name of the user as a string.
    """
    return os.getenv("USERS_REAL_NAME", "Unknown")

def get_users_email() -> str:
    """
    Returns the email of the user as a string.
    """
    return os.getenv("USERS_EMAIL", "Unknown")

def get_access_to_the_internet() -> str:
    """
    Returns 'True' if the system has access to the internet, otherwise 'False'.
    """
    try:
        socket.create_connection(("www.google.com", 80))
        return "True"
    except OSError:
        return "False"

def get_cpu_load() -> str:
    """
    Returns the current CPU load as a string percentage.
    """
    return f"{psutil.cpu_percent(interval=1)}%"

def get_ram_load() -> str:
    """
    Returns the current RAM load as a string percentage.
    """
    return f"{psutil.virtual_memory().percent}%"

print(get_ram_load())