import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
import numpy as np
import os
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier

# Load dataset
df = pd.read_csv("meal_data_categorized.csv")

# Encode categorical variables
diet_mapping = {"Vegetarian": 0, "Non-Vegetarian": 1, "Vegan": 2}
meal_mapping = {"Breakfast": 0, "Morning Snack": 1, "Lunch": 2, "Afternoon Snack": 3, "Dinner": 4}
df["diet_type"] = df["diet_type"].map(diet_mapping)
df["meal_category"] = df["meal_category"].map(meal_mapping)

# Train ML models
X = df[["calories", "protein", "carbs", "fat"]]
y_knn = df["meal_category"]
y_dt = df["diet_type"]

knn_model = KNeighborsClassifier(n_neighbors=5)
knn_model.fit(X, y_knn)

dt_model = DecisionTreeClassifier()
dt_model.fit(X, y_dt)


def save_diet_plan(username, weekly_plan):
    filename = f"{username}_diet_plan.csv"
    df_plan = pd.DataFrame(weekly_plan, columns=["Day", "Breakfast", "Morning Snack", "Lunch", "Afternoon Snack", "Dinner"])
    df_plan.to_csv(filename, index=False)

def load_diet_plan(username):
    filename = f"{username}_diet_plan.csv"
    if os.path.exists(filename):
        return pd.read_csv(filename).values.tolist()
    return None

def generate_diet():
    try:
        name = name_var.get().strip()
        diet_type = diet_var.get().strip()
        if not name or not diet_type:
            raise ValueError("Please enter a name and select a diet type.")
        
        diet_type_num = diet_mapping[diet_type]
        weekly_plan = []
        
        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            day_plan = [day]
            for category in meal_mapping.keys():
                meal_options = df[(df["meal_category"] == meal_mapping[category]) & (df["diet_type"] == diet_type_num)]
                if meal_options.empty:
                    day_plan.append("No Meal Available")
                else:
                    day_plan.append(meal_options.sample(1).iloc[0]["meal_name"])
            weekly_plan.append(day_plan)
        
        meal_table.delete(*meal_table.get_children())
        for day in weekly_plan:
            meal_table.insert("", "end", values=day)
        
        save_diet_plan(name, weekly_plan)
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Save user data
def save_user_data(name, age, gender, height, weight, activity, goal, diet_type):
    filename = "user_data.csv"
    new_data = pd.DataFrame([[name, age, gender, height, weight, activity, goal, diet_type]],
                             columns=["Name", "Age", "Gender", "Height", "Weight", "Activity", "Goal", "Diet Type"])
    
    if os.path.exists(filename):
        df_users = pd.read_csv(filename)
        df_users = pd.concat([df_users, new_data], ignore_index=True)
    else:
        df_users = new_data
    
    df_users.to_csv(filename, index=False)
    messagebox.showinfo("Success", "User data saved successfully!")

    
# Load user data
def load_user_data(name):
    filename = "user_data.csv"
    if os.path.exists(filename):
        df_users = pd.read_csv(filename)
        user_row = df_users[df_users["Name"] == name]
        if not user_row.empty:
            return user_row.iloc[0].tolist()
    return None

    
def load_last_diet():
    name = name_var.get().strip()
    if not name:
        messagebox.showerror("Error", "Please enter a name to load diet plan.")
        return
    last_plan = load_diet_plan(name)
    if last_plan:
        meal_table.delete(*meal_table.get_children())
        for day in last_plan:
            meal_table.insert("", "end", values=day)
    else:
        messagebox.showinfo("Info", "No previous diet plan found for this user.")

# Function to get exercise plan
def get_exercise_plan():
    exercise_plan = [
        ("Monday", "Push (Chest, Shoulders, Triceps)"),
        ("Tuesday", "Pull (Back, Biceps)"),
        ("Wednesday", "Legs (Quads, Hamstrings, Calves)"),
        ("Thursday", "Rest or Active Recovery"),
        ("Friday", "Upper Body Strength"),
        ("Saturday", "Lower Body Strength"),
        ("Sunday", "Rest or Cardio")
    ]

    exercise_table.delete(*exercise_table.get_children())

    for day, workout in exercise_plan:
        exercise_table.insert("", "end", values=(day, workout))



# Function to show progress
def show_progress():
    try:
        name = name_var.get().strip()
        age = int(age_var.get().strip())
        gender = gender_var.get().strip()
        height = int(height_var.get().strip())
        weight = int(weight_var.get().strip())
        activity = activity_var.get().strip()
        goal = goal_var.get().strip()

        if not name or not gender or not activity or not goal:
            raise ValueError("Please fill in all required fields.")

        # Activity multipliers
        activity_multiplier = {
            "Sedentary": 1.2,
            "Light": 1.375,
            "Moderate": 1.55,
            "Active": 1.725
        }

        # Calculate BMR
        bmr = (10 * weight + 6.25 * height - 5 * age + (5 if gender == "Male" else -161))
        daily_calories = bmr * activity_multiplier.get(activity, 1.2)

        # Adjust for goal
        calorie_adjustment = -500 if goal == "Lose Weight" else 500 if goal == "Gain Weight" else 0

        # Predict weight for 30 days
        predicted_weights = [weight]
        for _ in range(30):
            weight_change = calorie_adjustment / 7700  # 7700 kcal = 1kg change
            weight_fluctuation = np.random.uniform(-0.1, 0.1)  # Natural fluctuation
            predicted_weights.append(predicted_weights[-1] + weight_change + weight_fluctuation)

        # Generate graph
        plt.figure(figsize=(8, 5))
        plt.plot(range(31), predicted_weights, marker='o', linestyle='-', label="Predicted Weight", color="blue")

        plt.xlabel("Days")
        plt.ylabel("Weight (kg)")
        plt.title(f"Predicted Weight Change Over 30 Days ({goal})")
        plt.legend()
        plt.grid(True)
        plt.show()

    except Exception as e:
        messagebox.showerror("Error", str(e))


# GUI Setup
root = tk.Tk()
root.title("AI Diet Planner")
root.geometry("1000x700")

# User input fields
frame = tk.Frame(root)
frame.pack(padx=20, pady=20, anchor="w")

tk.Label(frame, text="Name:").grid(row=0, column=0, sticky="w", pady=2, padx=5)
name_var = tk.StringVar()
tk.Entry(frame, textvariable=name_var, width=30).grid(row=0, column=1, pady=2, padx=10)

tk.Label(frame, text="Age:").grid(row=1, column=0, sticky="w", pady=2, padx=5)
age_var = tk.StringVar()
tk.Entry(frame, textvariable=age_var, width=30).grid(row=1, column=1, pady=2, padx=10)

tk.Label(frame, text="Gender:").grid(row=2, column=0, sticky="w", pady=2, padx=5)
gender_var = ttk.Combobox(frame, values=["Male", "Female"], width=27)
gender_var.grid(row=2, column=1, pady=2, padx=10)

tk.Label(frame, text="Height (cm):").grid(row=3, column=0, sticky="w", pady=2, padx=5)
height_var = tk.StringVar()
tk.Entry(frame, textvariable=height_var, width=30).grid(row=3, column=1, pady=2, padx=10)

tk.Label(frame, text="Weight (kg):").grid(row=4, column=0, sticky="w", pady=2, padx=5)
weight_var = tk.StringVar()
tk.Entry(frame, textvariable=weight_var, width=30).grid(row=4, column=1, pady=2, padx=10)

tk.Label(frame, text="Activity Level:").grid(row=5, column=0, sticky="w", pady=2, padx=5)
activity_var = ttk.Combobox(frame, values=["Sedentary", "Light", "Moderate", "Active"], width=27)
activity_var.grid(row=5, column=1, pady=2, padx=10)

tk.Label(frame, text="Goal:").grid(row=6, column=0, sticky="w", pady=2, padx=5)
goal_var = ttk.Combobox(frame, values=["Lose Weight", "Maintain Weight", "Gain Weight"], width=27)
goal_var.grid(row=6, column=1, pady=2, padx=10)

tk.Label(frame, text="Diet Type:").grid(row=7, column=0, sticky="w", pady=2, padx=5)
diet_var = ttk.Combobox(frame, values=["Vegetarian", "Non-Vegetarian", "Vegan"], width=27)
diet_var.grid(row=7, column=1, pady=2, padx=10)

# Buttons
tk.Button(frame, text="Generate Diet Plan", command=generate_diet, width=25).grid(row=8, column=0, columnspan=2, pady=5, sticky="w", padx=5)
tk.Button(frame, text="Show Progress", command=show_progress, width=25).grid(row=9, column=0, columnspan=2, pady=5, sticky="w", padx=5)
tk.Button(frame, text="Get Exercise Plan", command=get_exercise_plan, width=25).grid(row=10, column=0, columnspan=2, pady=5, sticky="w", padx=5)

# Meal Table
meal_frame = tk.Frame(root)
meal_frame.pack(padx=20, pady=10, anchor="w")
tk.Label(meal_frame, text="Meal Plan", font=("Arial", 12, "bold")).pack(anchor="w")
meal_table = ttk.Treeview(meal_frame, columns=["Day", "Breakfast", "Morning Snack", "Lunch", "Afternoon Snack", "Dinner"], show="headings")
for col in ["Day", "Breakfast", "Morning Snack", "Lunch", "Afternoon Snack", "Dinner"]:
    meal_table.heading(col, text=col)
meal_table.pack(anchor="w")

# Exercise Table
exercise_frame = tk.Frame(root)
exercise_frame.pack(padx=20, pady=10, anchor="w")
tk.Label(exercise_frame, text="Exercise Plan", font=("Arial", 12, "bold")).pack(anchor="w")
exercise_table = ttk.Treeview(exercise_frame, columns=["Day", "Workout Type"], show="headings")
exercise_table.heading("Day", text="Day")
exercise_table.heading("Workout Type", text="Workout Type")
exercise_table.pack(anchor="w")

root.mainloop()