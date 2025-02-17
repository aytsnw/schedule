import customtkinter as ctk
import tkinter as tk
from schedule_calendar import Calendar



class Window(ctk.CTk):
    def __init__(self, name, main_window, title):
        super().__init__()
        self.name = name
        self.main = main_window
        self.title(title)
        self.set_geometry(self.main)

    def set_geometry(self, main_window):
        x = main_window.winfo_x()
        y = main_window.winfo_y()

        self.geometry("300x300+{}+{}".format(x + 720, y + 100))

    

class AddTask(Window):
    def __init__(self, name, route, calendar : Calendar, recurrency_cal : Calendar, main_window, title):
        super().__init__(name, main_window, title)
        self.route = route
        self.calendar = calendar
        self.recurrency_cal = recurrency_cal
        self.radio_state = False
        self.amount_entry_state = False
        self.protocol('WM_DELETE_WINDOW', lambda : self.route.alter_window_existence_state("add_task"))

    def enable_radio(self):
        if self.radio_state == True:
            self.btnY.configure(state="disabled")
            self.btnM.configure(state="disabled")
            self.btnW.configure(state="disabled")
            self.btnD.configure(state="disabled")
            self.radio_state = False

        else:
            self.btnY.configure(state="active")
            self.btnM.configure(state="active")
            self.btnW.configure(state="active")
            self.btnD.configure(state="active")
            self.radio_state = True


    def enable_rec_amount_entry(self, event):
        if self.amount_entry_state == True:
            self.amount_entry.pack_forget()
            self.amount_entry_state = False
        else:
            self.amount_entry_state = True
            self.amount_entry.pack()
            self.amount_entry.pack(before=self.label_desc)
    

    def display(self, current_task_name=None, message=None):
        label = ctk.CTkLabel(self, text="Task")
        label.pack()

        self.task_name_entry = ctk.CTkEntry(self, width=200, placeholder_text="task name...")
        self.task_name_entry.pack()

        self.task_name_entry.insert("end", current_task_name if current_task_name else "")

        self.bool_recurrency_var = tk.BooleanVar(self)
        btn = ctk.CTkCheckBox(self, text="Recurrent", variable=self.bool_recurrency_var, command=self.enable_radio)
        btn.bind("<Button-1>", self.enable_rec_amount_entry)
        btn.pack(ipady=5)

        radio_frame = ctk.CTkFrame(self)
        radio_frame.pack()

        self.str_recurrency_var = tk.StringVar(self, "year")
        self.btnY = tk.Radiobutton(radio_frame, text="Yearly", value="year", variable=self.str_recurrency_var)
        self.btnY.pack(side="left")
        self.btnM = tk.Radiobutton(radio_frame, text="Monthly", value="month", variable=self.str_recurrency_var)
        self.btnM.pack(side="left")
        self.btnW = tk.Radiobutton(radio_frame, text="Weekly", value="week", variable=self.str_recurrency_var)
        self.btnW.pack(side="left")
        self.btnD = tk.Radiobutton(radio_frame, text="Daily", value="day",variable=self.str_recurrency_var)
        self.btnD.pack(side="left")
        self.btnY.configure(state="disabled")
        self.btnM.configure(state="disabled")
        self.btnW.configure(state="disabled")
        self.btnD.configure(state="disabled")

        self.amount_entry = ctk.CTkEntry(self, width=35)

        self.label_desc = ctk.CTkLabel(self, text="Description")
        self.label_desc.pack()

        self.description_entry = ctk.CTkTextbox(self, height=100, width=200)
        self.description_entry.pack()

        self.add_btn  = ctk.CTkButton(self, text="Add task", command=lambda:
                                                            self.route.insert_to_db(self.task_name_entry.get(), 
                                                            self.description_entry.get("1.0", "end"), 
                                                            self.bool_recurrency_var.get(), 
                                                            self.str_recurrency_var.get(), 
                                                            self.amount_entry.get() if self.amount_entry else None))
        self.add_btn.pack()

        if message:
            label = tk.Label(self, text=message)
            label.pack()

        self.mainloop()
    


class EditTask(Window):
    def __init__(self, name, route, main_window, title):
        super().__init__(name, main_window, title)
        self.route = route
        self.protocol("WM_DELETE_WINDOW", lambda : self.route.alter_window_existence_state("edit_task"))
    
    def display(self, task_id, task_name, task_description, recurrency, task_status, message=None):

        label = tk.Label(self, text="Edit task name")
        label.pack()

        self.task_name_entry = tk.Entry(self, width=35)
        self.task_name_entry.pack()

        self.task_name_entry.insert("end", task_name)

        label = tk.Label(self, text="Edit description")
        label.pack()

        self.description_entry = tk.Text(self, height=8, width=35)
        self.description_entry.insert("1.0", task_description)
        self.description_entry.pack()

        if recurrency == 'true':
            self.bool_recurrency_var = tk.BooleanVar(self)

            btn_recurrency = tk.Checkbutton(self, text="Change all ocurrencies?", variable=self.bool_recurrency_var)
            btn_recurrency.pack()

        frame = tk.Frame(self)
        frame.pack()

        task_current_name = self.task_name_entry.get()
        task_current_description = self.description_entry.get("1.0", "end")

        if recurrency == 'true':
            btn_save = tk.Button(frame, text="Save changes", command= lambda : self.route.update_db(task_id, self.task_name_entry.get(), self.description_entry.get("1.0", "end"),
                                                                                       recurrency=self.bool_recurrency_var.get()))
        else:
            btn_save = tk.Button(frame, text="Save changes", command= lambda : self.route.update_db(task_id, self.task_name_entry.get(), self.description_entry.get("1.0", "end"),
                                                                                       recurrency=False))
    
        btn_save.pack(side="left")


        btn_cancel = tk.Button(frame, text="Cancel", command= lambda: self.route.alter_window_existence_state("edit_task"))
        btn_cancel.pack(side="left")

        if message:
            label = tk.Label(self, text=message)
            label.pack()

        self.mainloop()


     
class RemoveAll(Window):
    def __init__(self, name, route, main_window, title):
        super().__init__(name, main_window, title)
        self.route = route
        self.protocol("WM_DELETE_WINDOW", lambda : self.route.alter_window_existence_state("remove_all"))


    def display(self, id):
        frame = tk.Frame(self)
        frame.pack()

        label = tk.Label(frame, text="Remove all ocurrencies of this task?")
        label.pack()

        frame = tk.Frame(self)
        frame.pack()

        btn = tk.Button(frame, text="Yes", command= lambda : self.route.remove_from_db(id, remove_all=True))
        btn.pack(side="left")

        btn = tk.Button(frame, text="No", command= lambda : self.route.remove_from_db(id, remove_all=False))
        btn.pack(side="left")

        btn = tk.Button(frame, text="Cancel", command=lambda : self.route.alter_window_existence_state("remove_all"))
        btn.pack(side="left")

        self.mainloop()