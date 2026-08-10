import tkinter as tk
from tkinter import ttk, messagebox

from flood_app.schemas.recommendation import CHOICES, validate_num_people
from recommender import recommend_shelters


class ShelterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Flood Shelter Fuzzy Recommender")
        self.root.geometry("900x620")

        self._build_form()
        self._build_results()

    def _build_form(self):
        frame = ttk.LabelFrame(self.root, text="Input")
        frame.pack(fill="x", padx=14, pady=10)

        self.num_people = tk.StringVar(value="1")
        self.distance = tk.StringVar(value="medium")
        self.accessibility = tk.StringVar(value="moderate")
        self.elevation = tk.StringVar(value="medium")
        self.proximity = tk.StringVar(value="moderate")
        self.medical = tk.StringVar(value="basic")

        row1 = ttk.Frame(frame)
        row1.pack(fill="x", padx=10, pady=8)
        row2 = ttk.Frame(frame)
        row2.pack(fill="x", padx=10, pady=8)

        ttk.Label(row1, text="People").pack(side="left", padx=6)
        ttk.Entry(row1, textvariable=self.num_people, width=8).pack(side="left")

        self._combo(row1, "Distance", self.distance, CHOICES["distance_level"])
        self._combo(row1, "Accessibility", self.accessibility, CHOICES["accessibility_required"])
        self._combo(row2, "Elevation", self.elevation, CHOICES["elevation_input"])
        self._combo(row2, "Water Proximity", self.proximity, CHOICES["proximity_input"])
        self._combo(row2, "Medical", self.medical, CHOICES["medical_input"])

        ttk.Button(frame, text="Recommend Shelters", command=self.run_recommendation).pack(
            padx=12, pady=(2, 10), anchor="w"
        )

    def _combo(self, parent, label, variable, options):
        ttk.Label(parent, text=label).pack(side="left", padx=(14, 6))
        combo = ttk.Combobox(parent, textvariable=variable, values=options, width=12, state="readonly")
        combo.pack(side="left")

    def _build_results(self):
        frame = ttk.LabelFrame(self.root, text="Recommendations")
        frame.pack(fill="both", expand=True, padx=14, pady=(0, 12))

        self.best_label = ttk.Label(frame, text="Best match: -", font=("Segoe UI", 12, "bold"))
        self.best_label.pack(anchor="w", padx=12, pady=8)

        columns = ("name", "score", "distance", "beds", "access")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=17)
        self.tree.heading("name", text="Shelter")
        self.tree.heading("score", text="Score")
        self.tree.heading("distance", text="Distance (km)")
        self.tree.heading("beds", text="Available Beds")
        self.tree.heading("access", text="Accessibility")

        self.tree.column("name", width=220)
        self.tree.column("score", width=80, anchor="center")
        self.tree.column("distance", width=100, anchor="center")
        self.tree.column("beds", width=110, anchor="center")
        self.tree.column("access", width=110, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=12, pady=(0, 10))

    def run_recommendation(self):
        try:
            num_people = validate_num_people(self.num_people.get().strip())
        except ValueError:
            messagebox.showerror("Invalid Input", "People count must be a positive integer.")
            return

        data = recommend_shelters(
            num_people=num_people,
            distance_level=self.distance.get(),
            accessibility_required=self.accessibility.get(),
            elevation_input=self.elevation.get(),
            proximity_input=self.proximity.get(),
            medical_input=self.medical.get(),
        )

        for item in self.tree.get_children():
            self.tree.delete(item)

        if not data["recommendations"]:
            self.best_label.config(text="Best match: none")
            messagebox.showinfo("No Match", "No shelters matched your filters.")
            return

        best = data["best"]
        self.best_label.config(text=f"Best match: {best['name']} (score {best['score']})")

        for shelter in data["recommendations"]:
            self.tree.insert(
                "",
                "end",
                values=(
                    shelter["name"],
                    shelter["score"],
                    shelter["distance"],
                    shelter["available_beds"],
                    shelter["accessibility"],
                ),
            )


if __name__ == "__main__":
    root = tk.Tk()
    app = ShelterGUI(root)
    root.mainloop()
