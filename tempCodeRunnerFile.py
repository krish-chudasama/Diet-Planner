import pandas as pd
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier

# Load dataset
df = pd.read_csv("meal_data_categorized.csv")

diet_mapping = {"Vegetarian": 0, "Non-Vegetarian": 1, "Vegan": 2}
meal_mapping = {"Breakfast": 0, "Morning Snack": 1, "Lunch": 2, "Afternoon Snack": 3, "Dinner": 4}

df["diet_type"] = df["diet_type"].map(diet_mapping)
df["meal_category"] = df["meal_category"].map(meal_mapping)

X = df[["calories", "protein", "carbs", "fat"]]
y_knn = df["meal_category"]
y_dt = df["diet_type"]

knn_model = KNeighborsClassifier(n_neighbors=5)
knn_model.fit(X, y_knn)

dt_model = DecisionTreeClassifier()
dt_model.fit(X, y_dt)

# Database setup
def init_db():
    conn = sqlite3.connect("diet_planner.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            gender TEXT,
            height REAL,
            weight REAL,
            activity TEXT,
            goal TEXT,
            diet_preference TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_user_data(user_data):
    conn = sqlite3.connect("diet_planner.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (name, age, gender, height, weight, activity, goal, diet_preference)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", user_data)
    conn.commit()
    conn.close()

def generate_diet():
    try:
        name = name_var.get()
        age = int(age_var.get())
        gender = gender_var.get()
        height = int(height_var.get())
        weight = int(weight_var.get())
        activity = activity_var.get()
        goal = goal_var.get()
        diet_type = diet_var.get()

        if not name:
            messagebox.showerror("Error", "Name is required!")
            return

        diet_type_num = diet_mapping.get(diet_type, 0)
        user_data = (name, age, gender, height, weight, activity, goal, diet_type)
        save_user_data(user_data)

        weekly_plan = []
        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            day_plan = []
            for category in meal_mapping.keys():
                meal_options = df[(df["meal_category"] == meal_mapping[category]) & (df["diet_type"] == diet_type_num)]
                if not meal_options.empty:
                    selected_meal = meal_options.sample(1).iloc[0]["meal_name"]
                else:
                    selected_meal = "No Meal Available"
                day_plan.append(selected_meal)
            weekly_plan.append([day] + day_plan)

        for row in meal_table.get_children():
            meal_table.delete(row)
        for day in weekly_plan:
            meal_table.insert("", "end", values=day)

    except Exception as e:
        messagebox.showerror("Error", str(e))

# GUI Setup
init_db()
root = tk.Tk()
root.title("AI Diet Planner")
root.geometry("900x600")

tk.Label(root, text="Name:").grid(row=0, column=0)
name_var = tk.StringVar()
tk.Entry(root, textvariable=name_var).grid(row=0, column=1)

tk.Label(root, text="Age:").grid(row=1, column=0)
age_var = tk.StringVar()
tk.Entry(root, textvariable=age_var).grid(row=1, column=1)

tk.Label(root, text="Gender:").grid(row=2, column=0)
gender_var = tk.StringVar(value="Male")
tk.Radiobutton(root, text="Male", variable=gender_var, value="Male").grid(row=2, column=1)
tk.Radiobutton(root, text="Female", variable=gender_var, value="Female").grid(row=2, column=2)

tk.Label(root, text="Height (cm):").grid(row=3, column=0)
height_var = tk.StringVar()
tk.Entry(root, textvariable=height_var).grid(row=3, column=1)

tk.Label(root, text="Weight (kg):").grid(row=4, column=0)
weight_var = tk.StringVar()
tk.Entry(root, textvariable=weight_var).grid(row=4, column=1)

tk.Label(root, text="Physical Activity:").grid(row=5, column=0)
activity_var = ttk.Combobox(root, values=["Sedentary", "Light", "Moderate", "Active"])
activity_var.grid(row=5, column=1)

tk.Label(root, text="Goal:").grid(row=6, column=0)
goal_var = ttk.Combobox(root, values=["Lose Weight", "Maintain Weight", "Gain Weight"])
goal_var.grid(row=6, column=1)

tk.Label(root, text="Diet Type:").grid(row=7, column=0)
diet_var = ttk.Combobox(root, values=["Vegetarian", "Non-Vegetarian", "Vegan"])
diet_var.grid(row=7, column=1)

generate_button = tk.Button(root, text="Generate Diet Plan", command=generate_diet)
generate_button.grid(row=8, column=0, columnspan=2)

columns = ["Day", "Breakfast", "Morning Snack", "Lunch", "Afternoon Snack", "Dinner"]
meal_table = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    meal_table.heading(col, text=col)
    meal_table.column(col, width=140)
meal_table.grid(row=9, column=0, columnspan=2)

root.mainloop()
