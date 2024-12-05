from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import requests
from tkintermapview import TkinterMapView
import hashlib

# Data storage
search_history = []
saved_places = []

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to handle sign-up
def sign_up():
    username = username_entry_signup.get().strip()
    password = password_entry_signup.get().strip()
    if not username or not password:
        messagebox.showwarning("Input Error", "Please enter both username and password.")
        return
    if username in users_db:
        messagebox.showwarning("Username Taken", "This username is already taken.")
        return
    users_db[username] = hash_password(password)
    messagebox.showinfo("Success", "Sign up successful! You can now log in.")
    show_login_frame()

# Function to handle login
def login():
    username = username_entry_login.get().strip()
    password = password_entry_login.get().strip()
    if not username or not password:
        messagebox.showwarning("Input Error", "Please enter both username and password.")
        return
    if username not in users_db:
        messagebox.showwarning("Login Error", "Username not found. Please sign up.")
        return
    if users_db[username] != hash_password(password):
        messagebox.showwarning("Login Error", "Incorrect password.")
        return
    messagebox.showinfo("Success", "Login successful!")
    show_weather_frame()

# Function to switch to the sign-up frame
def show_sign_up_frame():
    login_frame.pack_forget()
    sign_up_frame.pack(pady=50)

# Function to switch to the login frame
def show_login_frame():
    sign_up_frame.pack_forget()
    login_frame.pack(pady=50)

# Function to switch to the weather app frame after login
def show_weather_frame():
    login_frame.pack_forget()
    weather_app_frame.pack(pady=50)
    weather()

# Create main window
root = tk.Tk()
root.title("Weather App - Login")
root.geometry("1000x700")
root.configure(bg="#EAF6F6")

# Initialize a dummy user database (username: hashed password)
users_db = {}

# --- Login Frame ---
login_frame = ttk.Frame(root)
username_label_login = ttk.Label(login_frame, text="Username:", font=("Verdana", 14))
username_label_login.pack(pady=10)
username_entry_login = ttk.Entry(login_frame, font=("Verdana", 14))
username_entry_login.pack(pady=10)
password_label_login = ttk.Label(login_frame, text="Password:", font=("Verdana", 14))
password_label_login.pack(pady=10)
password_entry_login = ttk.Entry(login_frame, font=("Verdana", 14), show="*")
password_entry_login.pack(pady=10)
login_button = ttk.Button(login_frame, text="Login", command=login, width=20)
login_button.pack(pady=20)
sign_up_link = ttk.Label(login_frame, text="Don't have an account? Sign up", font=("Verdana", 12, "italic"), foreground="blue", cursor="hand2")
sign_up_link.pack(pady=10)
sign_up_link.bind("<Button-1>", lambda e: show_sign_up_frame())

login_frame.pack(pady=50)

# --- Sign-Up Frame ---
sign_up_frame = ttk.Frame(root)
username_label_signup = ttk.Label(sign_up_frame, text="Username:", font=("Verdana", 14))
username_label_signup.pack(pady=10)
username_entry_signup = ttk.Entry(sign_up_frame, font=("Verdana", 14))
username_entry_signup.pack(pady=10)
password_label_signup = ttk.Label(sign_up_frame, text="Password:", font=("Verdana", 14))
password_label_signup.pack(pady=10)
password_entry_signup = ttk.Entry(sign_up_frame, font=("Verdana", 14), show="*")
password_entry_signup.pack(pady=10)
sign_up_button = ttk.Button(sign_up_frame, text="Sign Up", command=sign_up, width=20)
sign_up_button.pack(pady=20)
login_link = ttk.Label(sign_up_frame, text="Already have an account? Login", font=("Verdana", 12, "italic"), foreground="blue", cursor="hand2")
login_link.pack(pady=10)
login_link.bind("<Button-1>", lambda e: show_login_frame())

# --- Weather App Frame (Main Weather App) ---
weather_app_frame = ttk.Frame(root)

def format_time(timestamp, timezone_offset):
    """
    Converts a UTC timestamp to a formatted local time string.
    :param timestamp: UTC timestamp.
    :param timezone_offset: Timezone offset in seconds.
    :return: Local time in 'HH:MM:SS' format.
    """
    utc_time = datetime.utcfromtimestamp(timestamp)
    local_time = utc_time + timedelta(seconds=timezone_offset)
    return local_time.strftime("%H:%M:%S")

def get_weather(city):
    API_key = "505acde2d0a10122dab45b4063295614"
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_key}"
    try:
        res = requests.get(url)
        res.raise_for_status()  # Raise an HTTPError if the response code is not 200
        weather = res.json()
        
        icon_id = weather['weather'][0]['icon']
        temperature = weather['main']['temp'] - 273.15  # Convert from Kelvin to Celsius
        description = weather['weather'][0]['description']
        humidity = weather['main']['humidity']  # Add humidity
        wind_speed = weather['wind']['speed']  # Add wind speed
        city = weather['name']
        country = weather['sys']['country']
        lat = weather['coord']['lat']
        lon = weather['coord']['lon']

         # Extract sunrise and sunset times
        sunrise = datetime.utcfromtimestamp(weather['sys']['sunrise']).strftime('%H:%M:%S')
        sunset = datetime.utcfromtimestamp(weather['sys']['sunset']).strftime('%H:%M:%S')

        # Get current time
        timezone_offset = weather['timezone']

        icon_url = f"https://openweathermap.org/img/wn/{icon_id}@2x.png"
        return icon_url, temperature, description, humidity, wind_speed, city, country, lat, lon, sunrise, sunset, timezone_offset
    except requests.exceptions.Timeout:
        messagebox.showerror("Error", "Request timed out. Please check your internet connection.")
        return None
    except requests.exceptions.HTTPError:
        messagebox.showerror("Error", "City not found")
        return None
    except KeyError:
        messagebox.showerror("Error", "Unexpected response format")
        return None
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        return None

def generate_recommendation(description, temperature):
    if "rain" in description or "thunderstorm" in description:
        return "Stay indoors or carry an umbrella."
    elif "clear" in description or "sun" in description:
        if temperature > 30:
            return "Great weather for swimming or staying cool indoors."
        elif 20 <= temperature <= 30:
            return "Perfect for sightseeing or outdoor activities."
        else:
            return "Good for a light walk or scenic drive."
    elif "cloud" in description:
        return "Good for shopping or a casual outing."
    elif temperature < 10:
        return "It's cold outside, stay warm and limit outdoor activities."
    else:
        return "Weather is okay for general activities."

def generate_not_recommended(description, temperature):
    if "rain" in description or "thunderstorm" in description:
        return "Outdoor activities such as hiking or cycling are not recommended."
    elif "clear" in description or "sun" in description:
        if temperature > 35:
            return "Avoid prolonged exposure to the sun and strenuous outdoor activities."
        elif temperature < 5:
            return "Outdoor activities without proper warm clothing are not recommended."
    elif "cloud" in description:
        return "Star gazing or sunbathing is not recommended."
    elif temperature < 10:
        return "Outdoor water sports or light clothing are not recommended."
    else:
        return "No major restrictions, but always prepare for changing conditions."

def update_background(description):
    if "rain" in description or "thunderstorm" in description:
        root.configure(bg="#A4C8E1")  # Blueish for rain
    elif "clear" in description or "sun" in description:
        root.configure(bg="#FFE97F")  # Yellowish for sunny weather
    elif "cloud" in description:
        root.configure(bg="#D3D3D3")  # Gray for cloudy weather
    else:
        root.configure(bg="#FFFFFF")  # Default white background

def show_map_in_tab(lat, lon, city):
    map_widget.set_position(lat, lon)
    map_widget.set_zoom(12)
    map_widget.add_marker(lat, lon, text=city)

def search():
    city = city_entry.get().strip()
    if not city:
        messagebox.showwarning("Warning", "Please enter a city name")
        return

    result = get_weather(city)
    if result is None:
        return

    icon_url, temperature, description, humidity, wind_speed, city, country, lat, lon, sunrise, sunset, timezone_offset = result

    # Update weather information
    location_label.configure(text=f"{city}, {country}")
    image = Image.open(requests.get(icon_url, stream=True).raw)
    icon = ImageTk.PhotoImage(image)
    icon_label.configure(image=icon)
    icon_label.image = icon
    temperature_label.configure(text=f"Temperature: {temperature:.2f}°C")
    description_label.configure(text=f"Description: {description.capitalize()}")
    humidity_label.configure(text=f"Humidity: {humidity}%")
    wind_label.configure(text=f"Wind Speed: {wind_speed} m/s")
    sunrise_label.configure(text=f"Sunrise: {sunrise}")
    sunset_label.configure(text=f"Sunset: {sunset}")
    
    current_time = format_time(datetime.utcnow().timestamp(), timezone_offset)
    current_time_label.configure(text=f"Current Local Time: {current_time}")

    recommendation = generate_recommendation(description, temperature)
    recommendation_label.configure(text=f"Recommendation: {recommendation}")

    not_recommendation = generate_not_recommended(description, temperature)
    not_recommended_label.configure(text=f"Not Recommended: {not_recommendation}")

    # Update dynamic background based on weather
    update_background(description)

    # Update search history
    if city not in search_history:
        search_history.append(city)
        update_history()

    # Show the map in the map tab
    show_map_in_tab(lat, lon, city)

def update_history():
    for item in history_tree.get_children():
        history_tree.delete(item)
    for idx, city in enumerate(search_history, 1):
        history_tree.insert("", "end", values=(idx, city))

def add_to_saved():
    city = city_entry.get().strip()
    if not city:
        messagebox.showwarning("Warning", "Please enter a city name")
        return

    if city not in saved_places:
        saved_places.append(city)
        update_saved_places()
        messagebox.showinfo("Success", f"{city} added to saved places!")
    else:
        messagebox.showinfo("Info", f"{city} is already in your saved places.")

def update_saved_places():
    for item in saved_tree.get_children():
        saved_tree.delete(item)
    for idx, city in enumerate(saved_places, 1):
        saved_tree.insert("", "end", values=(idx, city))

def remove_saved_place():
    selected_item = saved_tree.selection()
    if not selected_item:
        messagebox.showwarning("Warning", "Please select a place to remove")
        return

    city = saved_tree.item(selected_item)["values"][1]
    saved_places.remove(city)
    update_saved_places()
    messagebox.showinfo("Success", f"{city} removed from saved places.")

def weather():
    # Custom styling
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", font=("Verdana", 14), rowheight=60, background="#F5F5F5", fieldbackground="#F5F5F5")
    style.configure("Treeview.Heading", font=("Verdana", 16, "bold"), background="#4F6272", foreground="white")
    style.map("Treeview", background=[('selected', '#B2DFDB')])
    style.configure("TButton", font=("Verdana", 12, "bold"), padding=10, relief="flat", background="#26A69A", foreground="white")
    style.map("TButton", background=[("active", "#00796B")])
    style.configure("TLabel", font=("Verdana", 14, "bold"), background="#EAF6F6", foreground="#2C3E50")

    # Tabs
    notebook = ttk.Notebook(weather_app_frame)
    notebook.pack(fill="both", expand=True, padx=20, pady=10)

    # Weather Search Tab
    search_tab = ttk.Frame(notebook)
    notebook.add(search_tab, text="🌦 Weather Search")

    search_frame = ttk.Frame(search_tab)
    search_frame.pack(pady=20)

    global city_entry
    city_entry = ttk.Entry(search_frame, font=("Verdana", 14), justify="center", width=18)
    city_entry.insert(0, "Enter city name...")
    city_entry.bind("<FocusIn>", lambda e: city_entry.delete(0, "end"))
    city_entry.pack(pady=10)

    search_button = ttk.Button(search_frame, text="🔍 Search", command=search, width=12)
    search_button.pack(pady=10)

    add_button = ttk.Button(search_frame, text="⭐ Add to Favorite", command=add_to_saved)
    add_button.pack(pady=10)

    # Results section
    global location_label, icon_label, temperature_label, description_label, humidity_label, wind_label, sunrise_label, sunset_label, current_time_label, recommendation_label, not_recommended_label
    location_label = tk.Label(search_tab, text="City: ", font=("Verdana", 12), bg="lightblue")    
    location_label.pack(pady=5)

    icon_label = tk.Label(search_tab, text="Icon: ", font=("Verdana", 12), bg="lightblue")
    icon_label.pack(pady=5)

    temperature_label = tk.Label(search_tab, text="Temperature: ", font=("Verdana", 12), bg="lightblue")
    temperature_label.pack(pady=5)

    description_label = tk.Label(search_tab, text="Description: ", font=("Verdana", 12), bg="lightblue")
    description_label.pack(pady=5)

    humidity_label = tk.Label(search_tab, text="Humidity: ", font=("Verdana", 12), bg="lightblue")
    humidity_label.pack(pady=5)

    wind_label = tk.Label(search_tab, text="Wind Speed: ", font=("Verdana", 12), bg="lightblue")
    wind_label.pack(pady=5)

    sunrise_label = tk.Label(search_tab, text="Sunrise: ", font=("Verdana", 12), bg="lightblue")
    sunrise_label.pack(pady=5)

    sunset_label = tk.Label(search_tab, text="Sunset: ", font=("Verdana", 12), bg="lightblue")
    sunset_label.pack(pady=5)

    current_time_label = ttk.Label(search_tab, text="Current Local Time: ", font=("Verdana", 12), background="lightblue")
    current_time_label.pack(pady=5)

    recommendation_label = tk.Label(search_tab, text="Recommendation: ", font=("Verdana", 12), bg="lightblue")
    recommendation_label.pack(pady=5)

    not_recommended_label = tk.Label(search_tab, text="Not Recommended: ", font=("Verdana", 12), bg="lightblue")
    not_recommended_label.pack(pady=5)

    # Map Tab
    map_tab = ttk.Frame(notebook)
    notebook.add(map_tab, text="🗺 Map View")

    global map_widget
    map_widget = TkinterMapView(map_tab, width=800, height=600, corner_radius=10)
    map_widget.pack(expand=True, fill="both")

    # Search History Tab
    history_tab = ttk.Frame(notebook)
    notebook.add(history_tab, text="📜 Search History")

    history_label = tk.Label(history_tab, text="Search History:", font=("Verdana", 16), bg="#EAF6F6")
    history_label.pack(pady=10)

    global history_tree
    history_tree = ttk.Treeview(history_tab, columns=("No", "City"), show="headings", height=15)
    history_tree.heading("No", text="No")
    history_tree.heading("City", text="City")
    history_tree.column("No", width=50, anchor="center")
    history_tree.column("City", width=300, anchor="w")
    history_tree.pack(pady=10, padx=20)

    # Favorite Places Tab
    saved_tab = ttk.Frame(notebook)
    notebook.add(saved_tab, text="⭐ Favorite Places")

    saved_label = tk.Label(saved_tab, text="Your Favorite Places:", font=("Verdana", 16), bg="#EAF6F6")
    saved_label.pack(pady=10)

    global saved_tree
    saved_tree = ttk.Treeview(saved_tab, columns=("No", "City"), show="headings", height=8)
    saved_tree.heading("No", text="No")
    saved_tree.heading("City", text="City")
    saved_tree.column("No", width=40, anchor="center")
    saved_tree.column("City", width=300, anchor="w")
    saved_tree.pack(pady=10, padx=20)

    remove_button = ttk.Button(saved_tab, text="🗑 Remove Selected Place", command=remove_saved_place)
    remove_button.pack(pady=10)

# Run the app
root.mainloop()