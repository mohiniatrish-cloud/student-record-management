import tkinter as tk
from tkinter import messagebox
import json
import os

# --- Data Storage ---
students = {}
DATA_FILE = "students_data.json"

# --- GUI Application Class ---
class StudentManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Management System")
        self.root.geometry("850x700")
        
        # Color Theme
        self.bg_blue = "#D4EBF8"   # Light blue background
        self.bg_cream = "#FDFBF7"  # Creamish details/form
        self.text_dark = "#333333"
        
        self.root.configure(bg=self.bg_blue)
        
        # 1. LOAD DATA ON STARTUP
        self.load_data()
        
        # --- Top Menu Bar ---
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        action_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_cream)
        action_menu.add_command(label="Show All Records", command=self.view_all_popup)
        action_menu.add_command(label="Search Student", command=self.search_popup)
        # NEW: Edit Student added to the menu
        action_menu.add_command(label="Edit Student", command=self.edit_prompt_popup)
        action_menu.add_command(label="Delete Student", command=self.delete_popup)
        action_menu.add_separator()
        action_menu.add_command(label="Exit", command=self.root.quit)
        
        menubar.add_cascade(label="Menu", menu=action_menu)

        # Centered Input
        self.form_frame = tk.Frame(self.root, bg=self.bg_cream, padx=50, pady=40, relief=tk.RAISED, borderwidth=2)
        self.form_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        title_label = tk.Label(self.form_frame, text="Add Student Details", font=("Helvetica", 18, "bold"), bg=self.bg_cream, fg=self.text_dark)
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        self.roll_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.age_var = tk.StringVar()
        self.course_var = tk.StringVar()
        self.eng_var = tk.StringVar()
        self.hindi_var = tk.StringVar()
        self.math_var = tk.StringVar()
        self.sci_var = tk.StringVar()
        self.sst_var = tk.StringVar()

        self.entries = []

        self.add_field("Roll Number:", self.roll_var, 1)
        self.add_field("Name:", self.name_var, 2)
        self.add_field("Age:", self.age_var, 3)
        self.add_field("Course (e.g., BCA):", self.course_var, 4)
        self.add_field("English Marks:", self.eng_var, 5)
        self.add_field("Hindi Marks:", self.hindi_var, 6)
        self.add_field("Math Marks:", self.math_var, 7)
        self.add_field("Science Marks:", self.sci_var, 8)
        self.add_field("SST Marks:", self.sst_var, 9)

        for i in range(len(self.entries) - 1):
            self.entries[i].bind('<Return>', lambda event, next_entry=self.entries[i+1]: next_entry.focus())
        self.entries[-1].bind('<Return>', lambda event: self.add_student())

        submit_btn = tk.Button(self.form_frame, text="Submit", command=self.add_student, bg=self.bg_blue, fg=self.text_dark, font=("Helvetica", 12, "bold"), width=20, relief=tk.FLAT, activebackground="#A7C7E7")
        submit_btn.grid(row=10, column=0, columnspan=2, pady=(25, 0))
        
        self.entries[0].focus()

    # --- Data Persistence Functions ---
    def load_data(self):
        global students
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f:
                    students = json.load(f)
            except json.JSONDecodeError:
                students = {}

    def save_data(self):
        with open(DATA_FILE, "w") as f:
            json.dump(students, f, indent=4)

    # --- Helper Functions ---
    def add_field(self, label_text, variable, row_num):
        label = tk.Label(self.form_frame, text=label_text, bg=self.bg_cream, font=("Helvetica", 11, "bold"))
        label.grid(row=row_num, column=0, sticky="e", pady=8, padx=10)
        
        entry = tk.Entry(self.form_frame, textvariable=variable, font=("Helvetica", 11), width=25, relief=tk.SOLID, borderwidth=1, bg="#FFFFFF")
        entry.grid(row=row_num, column=1, pady=8, padx=10)
        self.entries.append(entry)

    # --- Core Logic & Validation ---
    def validate_marks(self, *marks):
        for mark in marks:
            if not (0 <= mark <= 100):
                return False
        return True

    def add_student(self):
        roll_no = self.roll_var.get().strip()
        if not roll_no:
            messagebox.showerror("Error", "Roll Number is required!")
            return

        if roll_no in students:
            messagebox.showerror("Error", f"Student with Roll Number '{roll_no}' already exists!")
            return

        # 2. DATA VALIDATION
        age_str = self.age_var.get().strip()
        if not age_str.isdigit() or int(age_str) <= 0:
            messagebox.showerror("Input Error", "Age must be a valid positive number.")
            return

        name = self.name_var.get().strip()
        course = self.course_var.get().strip()
        if not name or not course:
            messagebox.showerror("Input Error", "Name and Course cannot be empty.")
            return

        try:
            eng = int(self.eng_var.get())
            hindi = int(self.hindi_var.get())
            math = int(self.math_var.get())
            science = int(self.sci_var.get())
            sst = int(self.sst_var.get())

            if not self.validate_marks(eng, hindi, math, science, sst):
                messagebox.showerror("Input Error", "Marks must be between 0 and 100.")
                return

            per = (eng + hindi + math + science + sst) / 5
            division = "First" if per >= 60 else "Second" if per >= 50 else "Third"
            grade = "A" if per >= 90 else "B" if per >= 80 else "C" if per >= 70 else "D" if per >= 60 else "F"

            students[roll_no] = {
                "name": name,
                "age": age_str,
                "course": course,
                "percentage": per,
                "division": division,
                "grade": grade,
                "marks": {"eng": eng, "hindi": hindi, "math": math, "sci": science, "sst": sst}
            }

            # Save to permanent file
            self.save_data()

            messagebox.showinfo("Success", "Student added successfully to the record!")
            self.clear_fields()
            self.entries[0].focus()

        except ValueError:
            messagebox.showerror("Input Error", "Please ensure all marks are entered as valid numbers (no text).")

    # --- 3. EDIT STUDENT LOGIC ---
    def edit_prompt_popup(self):
        prompt_win = tk.Toplevel(self.root)
        prompt_win.title("Edit Student")
        prompt_win.geometry("350x200")
        prompt_win.configure(bg=self.bg_blue)
        
        tk.Label(prompt_win, text="Enter Roll Number to Edit:", bg=self.bg_blue, font=("Helvetica", 11, "bold")).pack(pady=15)
        r_entry = tk.Entry(prompt_win, font=("Helvetica", 11))
        r_entry.pack(pady=5)
        r_entry.focus()
        
        def open_edit_form():
            r = r_entry.get().strip()
            if r in students:
                prompt_win.destroy()
                self.populate_edit_form(r)
            else:
                messagebox.showerror("Not Found", "Student not found!", parent=prompt_win)

        tk.Button(prompt_win, text="Find Student", command=open_edit_form, bg=self.bg_cream, font=("Helvetica", 10, "bold")).pack(pady=10)

    def populate_edit_form(self, roll_no):
        details = students[roll_no]
        
        # Fill the main form with existing data
        self.roll_var.set(roll_no)
        self.name_var.set(details["name"])
        self.age_var.set(details["age"])
        self.course_var.set(details["course"])
        
        # Handle backward compatibility if old records don't have individual marks saved
        if "marks" in details:
            self.eng_var.set(details["marks"]["eng"])
            self.hindi_var.set(details["marks"]["hindi"])
            self.math_var.set(details["marks"]["math"])
            self.sci_var.set(details["marks"]["sci"])
            self.sst_var.set(details["marks"]["sst"])
        
        # Briefly remove the student so "Submit" acts as an overwrite
        del students[roll_no]

    # --- Popup Windows from Menu ---
    def view_all_popup(self):
        popup = tk.Toplevel(self.root)
        popup.title("All Student Records")
        popup.geometry("650x450")
        popup.configure(bg=self.bg_blue)

        title = tk.Label(popup, text="System Records", font=("Helvetica", 16, "bold"), bg=self.bg_blue, fg=self.text_dark)
        title.pack(pady=15)

        text_area = tk.Text(popup, bg=self.bg_cream, font=("Courier", 10), relief=tk.GROOVE, borderwidth=2)
        text_area.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        if not students:
            text_area.insert(tk.END, "No students found in the system.\n")
        else:
            for r_no, details in students.items():
                record = (f"Roll No: {r_no} | Name: {details['name']} | Age: {details['age']} | Course: {details['course']}\n"
                          f"Marks: {details['percentage']}% | Div: {details['division']} | Grade: {details['grade']}\n"
                          f"{'-'*65}\n")
                text_area.insert(tk.END, record)
        
        text_area.config(state=tk.DISABLED)

    def search_popup(self):
        search_win = tk.Toplevel(self.root)
        search_win.title("Search Student")
        search_win.geometry("350x200")
        search_win.configure(bg=self.bg_blue)
        
        tk.Label(search_win, text="Enter Roll Number:", bg=self.bg_blue, font=("Helvetica", 11, "bold")).pack(pady=15)
        s_entry = tk.Entry(search_win, font=("Helvetica", 11))
        s_entry.pack(pady=5)
        s_entry.focus()
        
        def do_search():
            r = s_entry.get().strip()
            if r in students:
                details = students[r]
                msg = f"Name: {details['name']}\nCourse: {details['course']}\nPercentage: {details['percentage']}%\nGrade: {details['grade']}"
                messagebox.showinfo("Student Found", msg, parent=search_win)
                search_win.destroy()
            else:
                messagebox.showerror("Not Found", "Student not found!", parent=search_win)

        tk.Button(search_win, text="Search", command=do_search, bg=self.bg_cream, font=("Helvetica", 10, "bold")).pack(pady=10)

    def delete_popup(self):
        del_win = tk.Toplevel(self.root)
        del_win.title("Delete Student")
        del_win.geometry("350x200")
        del_win.configure(bg=self.bg_blue)
        
        tk.Label(del_win, text="Enter Roll Number to Delete:", bg=self.bg_blue, font=("Helvetica", 11, "bold")).pack(pady=15)
        d_entry = tk.Entry(del_win, font=("Helvetica", 11))
        d_entry.pack(pady=5)
        d_entry.focus()
        
        def do_delete():
            r = d_entry.get().strip()
            if r in students:
                del students[r]
                self.save_data()  # Save changes to file
                messagebox.showinfo("Deleted", f"Student with Roll No '{r}' deleted successfully.", parent=del_win)
                del_win.destroy()
            else:
                messagebox.showerror("Not Found", "Student not found!", parent=del_win)

        tk.Button(del_win, text="Delete", command=do_delete, bg=self.bg_cream, font=("Helvetica", 10, "bold")).pack(pady=10)

    def clear_fields(self):
        self.roll_var.set("")
        self.name_var.set("")
        self.age_var.set("")
        self.course_var.set("")
        self.eng_var.set("")
        self.hindi_var.set("")
        self.math_var.set("")
        self.sci_var.set("")
        self.sst_var.set("")

# --- Run Application ---
if __name__ == "__main__":
    root = tk.Tk()
    app = StudentManagementApp(root)
    root.mainloop()