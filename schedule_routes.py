import customtkinter as ctk
import tkinter as tk
from datetime import datetime
from schedule_calendar import Calendar
from windows import AddTask, EditTask, RemoveAll
from sqlalchemy import text



class Route():

    def __init__(self, name : str, master, engine):
        self.name = name
        self.master = master
        self.engine = engine


    def set_main_frame(self):
        self.main_frame = ctk.CTkFrame(self.master, height=530, width=500, corner_radius=10) 
        self.main_frame.grid(row=2, column=0)
        self.main_frame.pack_propagate(False)


    def redirect(self, event, route_name : str, date : datetime):
        print("redirecting to route: {}".format(route_name))
        if route_name == "day_page":
            self.calendar.set_index(custom_date=date)
            self.master.render_page(route_name)
        if route_name == "week_page":
            print("todo")
        if route_name== "month_page":
            print("todo")

class Day(Route):
    def __init__(
                self, 
                 name, 
                 calendar : Calendar, 
                 master,
                 recurrency_cal : Calendar,
                 engine
                 ):
        super().__init__(name, master, engine)
        self.calendar = calendar
        self.recurrency_cal = recurrency_cal
        self.add_task_window_check = False
        self.edit_task_window_check = False
        self.remove_all_window_check = False

    def create_window(self, window_name : str=None, **kwargs):

        if window_name == "add_task":
            if self.add_task_window_check:
                self.add_task_window.destroy()
                self.add_task_window_check = False
            self.add_task_window = AddTask("add_task", self, self.calendar, self.recurrency_cal, self.master, "Add a new task!")
            self.master.add_window(self.add_task_window)
            self.add_task_window_check = True

        elif window_name == "edit_task":
            if self.edit_task_window_check:
                self.edit_task_window.destroy()
                self.edit_task_window_check= False
            self.edit_task_window = EditTask("edit_task", self, self.master,"Manage task")
            self.master.add_window(self.edit_task_window)
            self.edit_task_window_check = True
            

        elif window_name == "remove_all":
            if self.remove_all_window_check:
                self.remove_all_window.destroy()
                self.remove_all_window_check = False
            self.remove_all_window = RemoveAll("remove_all", self, self.master, "Remove Recurrencies")
            self.master.add_window(self.remove_all_window)
            self.remove_all_window_check = True

        else:
            raise ValueError("bad window name, try: ['add_task' | 'edit_task' | 'remove_all']")

    
    def alter_window_existence_state(self, window_name : str=None):
        if window_name == "add_task":
            if self.add_task_window_check:
                self.add_task_window.destroy()
                self.add_task_window_check = False
            else:
                return
        elif window_name == "edit_task":
            if self.edit_task_window_check:
                self.edit_task_window.destroy()
                self.edit_task_window_check = False
            else:
                return
        elif window_name == "remove_all":
            if self.remove_all_window_check:
                self.remove_all_window.destroy()
                self.remove_all_window_check = False
            else:
                return
        else:
            raise ValueError("bad window_name, try: ['add_task' | 'edit_task' | 'remove_all']")


    @property
    def today(self):
        return self.calendar.get_today()


    def refresh(self, message=None):
        self.master.render_page(self.name, message=message)


    def display_edit_task_window(self, event, task_id, message=None):
        self.create_window("edit_task")
        result = self.engine.execute(text("SELECT task, description, recurrent, status FROM tasks WHERE id = {}".format(task_id)))
        rows = result.fetchone()
        task_name = rows[0]
        task_description = rows[1]
        recurrency = rows[2]
        print(recurrency)
        task_status = rows[3]
        self.edit_task_window.display(task_id, task_name, task_description, recurrency, task_status, message=message)

    def display_add_task_window(self, event=None, current_task_name=None, message : str=None):
        self.create_window("add_task")
        self.add_task_window.display(message=message)


    def display_remove_all_window(self, id):
        self.create_window("remove_all")
        self.remove_all_window.display(id)
        

    def prev_day(self):
        self.calendar.update_index("day", amount=-1)
        self.refresh()
    

    def next_day(self):
        self.calendar.update_index("day", amount=1)
        self.refresh()
    

    def set_bottom_nav_frame(self):
        self.nav_bot = ctk.CTkFrame(self.master, fg_color="transparent")
        self.nav_bot.grid(row=3, column=0, sticky="we")

        self.bot_btn_container = ctk.CTkFrame(self.nav_bot, width=500, height=50, fg_color="transparent")
        self.bot_btn_container.pack()
        self.bot_btn_container.grid_propagate(False)
        self.bot_btn_container.grid_columnconfigure(0, weight=1)
        self.bot_btn_container.grid_columnconfigure(1, weight=1)
        self.bot_btn_container.grid_columnconfigure(2, weight=1)
        self.bot_btn_container.grid_rowconfigure(0, weight=1)


        btn = ctk.CTkButton(self.bot_btn_container, text="ᐊ", command= lambda : self.prev_day(), width=5)
        btn.grid(row=0, column=0, sticky="w")

        btn = ctk.CTkButton(self.bot_btn_container, text="New Task!", command=self.display_add_task_window)
        btn.grid(row=0, column=1)

        btn = ctk.CTkButton(self.bot_btn_container, text="ᐅ", command= lambda : self.next_day(), width=5)
        btn.grid(row=0, column=2, sticky="e")


    def task_done(self, id):
        self.engine.execute(text("UPDATE tasks SET status = 'done' WHERE id = {}".format(id)))
        self.engine.commit()
        self.refresh()
    

    def undo_task_done(self, id):
        self.engine.execute(text("UPDATE tasks SET status = 'pending' WHERE id = {}".format(id)))
        self.engine.commit()
        self.refresh()


    def indices_by_day_enum(self, month : list, day_enum) -> dict | None:
        for week_index, week in enumerate(month):
            for day_index, day in enumerate(week):
                if int(day.strftime("%d")) == day_enum:
                    return {"week_index": week_index, "day_index": day_index}    


    def insert_to_db(
                    self,
                    task,
                    description,
                    recurrency : bool,
                    recurrency_mode, 
                    recurrency_amount : str, 
                    ) -> None:
        today = self.today
        
        if not task:
            print("task not found")
            return self.display_add_task_window(message="You must write a task!")
        
        if not recurrency:
            day = int(today.strftime("%d"))
            month = int(today.strftime("%m"))
            year = int(today.strftime("%Y"))
            self.engine.execute(text("INSERT INTO tasks (task, description, recurrent, recurrency_type, recurrency_amount, day, month, year) VALUES('{}', '{}', 'false', NULL, NULL, {}, {}, {})".format(task, description, day, month, year)))
            result = self.engine.execute(text("SELECT id FROM tasks ORDER BY id DESC"))
            rows_tsk = result.fetchone()
            self.engine.execute(text("INSERT INTO tasks_recurrencies (task_id, recurrency_id) VALUES({}, NULL)".format(rows_tsk[0])))
            self.engine.commit()

        else:
            if not recurrency_amount.isdigit() or recurrency_amount == None:
                return self.display_add_task_window(current_task_name=task, message="Choose a valid recurrency amount!")
            recurrency_amount = int(recurrency_amount)
            self.recurrency_cal.set_index(custom_date=today)
            week_day_index = int(today.strftime("%w")) - 1
            self.engine.execute(text("INSERT INTO recurrencies (id) VALUES(NULL)"))
            result = self.engine.execute(text("SELECT id FROM recurrencies ORDER BY id DESC LIMIT 1"))
            rows_rec = result.fetchone()
            today_fixed = int(self.recurrency_cal.get_today().strftime("%d"))
            month_index = int(self.recurrency_cal.get_today().strftime("%m")) - 1
            for _ in range(recurrency_amount):
                today = self.recurrency_cal.get_today()
                day = int(today.strftime("%d"))
                month = int(today.strftime("%m"))
                year = int(today.strftime("%Y"))
                self.engine.execute(text("INSERT INTO tasks (task, description, recurrent, recurrency_type, recurrency_amount, day, month, year) VALUES('{}', '{}', 'true', '{}', {}, {}, {}, {})".format(task, description, recurrency_mode, recurrency_amount, day, month, year)))
                result = self.engine.execute(text("SELECT id FROM tasks ORDER BY id DESC"))
                rows_tsk = result.fetchone()
                self.engine.execute(text("INSERT INTO tasks_recurrencies (task_id, recurrency_id) VALUES({}, {})".format(rows_tsk[0], rows_rec[0])))
                
                if self.recurrency_cal.update_index(recurrency_mode, amount=1):
                    if recurrency_mode == "week":
                        self.recurrency_cal.update_index("day", set=week_day_index)
                    elif recurrency_mode == "month":
                        dict = self.indices_by_day_enum(self.recurrency_cal.get_this_month(), today_fixed)
                        day_index = dict["day_index"]
                        week_index = dict["week_index"]
                        self.recurrency_cal.update_index("week", set=week_index)
                        self.recurrency_cal.update_index("day", set=day_index)
                    elif recurrency_mode == "year":
                        self.recurrency_cal.update_index("month", set=month_index)
                        dict = self.indices_by_day_enum(self.recurrency_cal.get_this_month(), today_fixed)
                        day_index = dict["day_index"]
                        week_index = dict["week_index"]
                        self.recurrency_cal.update_index("week", set=week_index)
                        self.recurrency_cal.update_index("day", set=day_index)
                else:
                    self.alter_window_existence_state("add_task")
                    return self.master.render_page("day_page", message="You've gone too far! The current version doesn't support date beyond {}".format(2025 + self.calendar.year_index_limit))
            self.engine.commit()

        self.refresh(message="Let's go! Task added.")
        self.alter_window_existence_state("add_task")


    def remove_from_db(self, id, remove_all : bool):
        if remove_all == True:
            result = self.engine.execute(text("SELECT recurrency_id from tasks_recurrencies WHERE task_id = {}".format(id)))
            rows = result.fetchone()
            recurrency_id = None
            if rows:
                recurrency_id = rows[0]
            else:
                self.alter_window_existence_state("remove_all")
                raise ValueError("Task not found")
            self.engine.execute(text("DELETE FROM tasks WHERE id IN (SELECT task_id FROM tasks_recurrencies WHERE recurrency_id = {})".format(recurrency_id)))
            
        else:
            self.engine.execute(text("DELETE FROM tasks WHERE id = {}".format(id)))

        self.alter_window_existence_state("remove_all")
        self.engine.commit()
        self.refresh()


    def update_db(self, task_id, task_name, task_description, recurrency : bool):

        if not task_name:
            return self.display_edit_task_window(None, task_id, message="Task name can't be blank")

        result = self.engine.execute(text("SELECT recurrency_id FROM tasks_recurrencies WHERE task_id = {}".format(task_id)))
        rows = result.fetchone()
        if rows:
            recurrency_id = rows[0]
            

        if  recurrency == True:
            self.engine.execute(text("UPDATE tasks SET task = '{}', description = '{}' WHERE id IN (SELECT task_id FROM tasks_recurrencies WHERE recurrency_id = {})".format(task_name,
                                                                                                                                                               task_description,
                                                                                                                                                               recurrency_id)))
        elif recurrency == False:
            self.engine.execute(text("UPDATE tasks SET task = '{}', description = '{}' WHERE id = {}".format(task_name, task_description, task_id)))

        self.alter_window_existence_state("edit_task")
        self.engine.commit()
        self.refresh()


    
    def display_tasks(self):
            day = int(self.today.strftime("%d"))
            month = int(self.today.strftime("%m"))
            year = int(self.today.strftime("%Y"))


            result = self.engine.execute(text("SELECT id, task, recurrent, status FROM tasks WHERE day = {} AND month = {} AND year = {}".format(day, month, year)))
            rows = result.fetchall()

            total_children = len(self.day_items_container.winfo_children())

            for i in range(len(rows)):
                task_id = int(rows[i][0])

                task_recurrent = rows[i][2]
                task_status = rows[i][3]

                day_item_frame = ctk.CTkFrame(self.pending_container if task_status == 'pending' else self.done_container, fg_color="transparent", height=20, width=480, corner_radius=10)
                day_item_frame.pack(pady=2)
                day_item_frame.pack_propagate(False)

                item_text = rows[i][1]

                item_text_frame = ctk.CTkButton(day_item_frame, text=item_text, height=20, width=370, corner_radius=5, fg_color="#336633" if task_status == "done" else "#333333", hover_color="white", anchor="w")
                item_text_frame.bind("<Button-1>", lambda event, task_id=task_id: self.display_edit_task_window(event, task_id))
                item_text_frame.pack(side="left")
                item_text_frame.pack_propagate(False)

                item_btn_frame = ctk.CTkFrame(day_item_frame, height=20, width=60, fg_color="transparent")
                item_btn_frame.pack(side="right")
    

                if task_status == "pending":
                    btn = ctk.CTkButton(item_btn_frame, text="✔", command= lambda id=task_id : self.task_done(id), width=5)
                    btn.pack(side="right")
                else:
                    btn = ctk.CTkButton(item_btn_frame, text='⮌', command= lambda id=task_id : self.undo_task_done(id), width=5)
                    btn.pack(side="right")

                if task_recurrent == 'true':
                    btn = ctk.CTkButton(item_btn_frame, text="X", fg_color="red", command= lambda id=task_id: self.display_remove_all_window(id), width=3)       
                else:
                    btn = ctk.CTkButton(item_btn_frame, text="X", fg_color="red", command= lambda id=task_id : self.remove_from_db(id, remove_all=False), width=3)

                btn.pack(side="right")


    def display(self, message=None):
        self.calendar.print_current_index()
        self.set_main_frame()

        title_container = ctk.CTkFrame(self.main_frame, height=20, width=460, corner_radius=10, fg_color="transparent")
        title_container.pack()

        top_frame = ctk.CTkFrame(title_container, width=450, height=50)
        top_frame.pack()
        top_frame.pack_propagate(False)

        frame_1 = ctk.CTkFrame(top_frame)
        frame_1.pack(side="left")

        label = ctk.CTkLabel(frame_1, text="{}".format(self.today.strftime("%A")), font=("<family-font>", 27))
        label.pack(padx=10)

        frame_2 = ctk.CTkFrame(top_frame, fg_color="transparent")
        frame_2.pack(side="right")

        label = ctk.CTkLabel(frame_2, text="{}, {}".format(self.today.strftime("%B"), self.today.strftime("%d")), fg_color="transparent", height=50)
        label.pack(padx=10)

        if message:
            bottom_frame = ctk.CTkFrame(title_container, height=10)
            bottom_frame.pack()
            label = ctk.CTkLabel(bottom_frame, text=message, font=("",10), height=10)
            label.pack()

        if self.calendar.check_datetime_correspondency(self.calendar.get_today(real=True), self.calendar.get_today()):    
            label = ctk.CTkLabel(top_frame, text="Today ☀", height=50, font=("family_font", 22))
            label.pack()

        self.day_items_container = ctk.CTkFrame(self.main_frame, width=460, height=480, fg_color="#444444", corner_radius=10)
        self.day_items_container.pack(padx=10, pady=10)
        self.day_items_container.pack_propagate(False)

        self.pending_container = ctk.CTkFrame(self.day_items_container, height=1, fg_color="transparent")
        self.pending_container.pack(padx=5, pady=5)

        self.done_container = ctk.CTkFrame(self.day_items_container, height=1, fg_color="transparent")
        self.done_container.pack(padx=5, pady=5)

        self.display_tasks()
        self.set_bottom_nav_frame()



class Week(Route):
    def __init__(self, name, calendar : Calendar, master, engine):
        super().__init__(name, master, engine)
        self.calendar = calendar


    @property
    def today(self):
        return self.calendar.get_today()
    
    
    @property
    def real_today(self):
        return self.calendar.get_today(real=True)
    

    @property
    def this_week(self):
        return self.calendar.get_this_week()
    

    @property
    def this_week_index(self):
        return self.calendar.get_this_week("index")


    def set_title_container(self):
        today = self.today
        title_frame = ctk.CTkFrame(self.main_frame, width=1000, height=40, fg_color="transparent")
        title_frame.grid(row=0, column=0, columnspan=7)
        title_frame.pack_propagate(False)

        date_text = ctk.CTkLabel(title_frame, text="{}, {}".format(today.strftime("%B"), today.strftime("%Y")), font=("", 20), height=40)
        date_text.pack(ipadx=30)
    

    def set_bottom_nav_frame(self):

        self.nav_bot = ctk.CTkFrame(self.master, fg_color="transparent")
        self.nav_bot.grid(row=3, column=0, sticky="we")

        self.bot_btn_container = ctk.CTkFrame(self.nav_bot, width=500, height=50, fg_color="transparent")
        self.bot_btn_container.pack()
        self.bot_btn_container.grid_propagate(False)
        self.bot_btn_container.grid_columnconfigure(0, weight=1)
        self.bot_btn_container.grid_columnconfigure(1, weight=1)
        self.bot_btn_container.grid_columnconfigure(2, weight=1)
        self.bot_btn_container.grid_rowconfigure(0, weight=1)

        btn = ctk.CTkButton(self.bot_btn_container, text="<", command= lambda : self.prev_week(), width=5)
        btn.pack(side="left")

        btn = ctk.CTkButton(self.bot_btn_container, text=">", command= lambda : self.next_week(), width=5)
        btn.pack(side="left")
        

    def prev_week(self):
        self.calendar.update_index("week", amount=-1)
        self.master.render_page(self.name)
    

    def next_week(self):
        self.calendar.update_index("week", amount=1)
        self.master.render_page(self.name)


    def display(self):

        self.weekday_interior = []

        self.set_main_frame()
        self.set_title_container()

        self.calendar.print_current_index()
        year_index = self.calendar.year_index
        month_index = self.calendar.month_index
        week_index = self.calendar.week_index

        def on_hover(event, index):
           self.weekday_interior[index].configure(fg_color="white")
        

        def on_leave(event, color, index):
            self.weekday_interior[index].configure(fg_color=color)


        self.set_title_container()

        for i in range(len(self.this_week)):
                result = self.engine.execute(text("SELECT id, task, status FROM tasks WHERE day = {} AND month = {} AND year={}".format(
                    int(self.this_week[i].strftime("%d")), int(self.this_week[i].strftime("%m")), int(self.this_week[i].strftime("%Y")))))

                rows = result.fetchall()

                weekday_name = self.this_week[i].strftime("%A")
                day_enum = self.this_week[i].strftime("%d")

                self.weekday_frame = ctk.CTkFrame(self.main_frame, height=300, width=200, corner_radius=0, fg_color="#333333")
                self.weekday_frame.grid(row=1, column=i)
                self.weekday_frame.pack_propagate(False)

                top_frame = ctk.CTkFrame(self.weekday_frame, fg_color="transparent", width=200, height=20)
                top_frame.pack()
                top_frame.pack_propagate(False)
                top_frame.pack_configure(padx=45, pady=5)

                main_frame = ctk.CTkFrame(self.weekday_frame, width=300, height=280, fg_color="#272727")
                self.weekday_interior.append(main_frame)
                main_frame.bind("<Button-1>", lambda event, route_name="day_page", date=self.calendar.years[year_index][month_index][week_index][i] : self.redirect(event, route_name, date))
                main_frame.bind("<Enter>", lambda event, index=i : on_hover(event, index))
                main_frame.pack()
                main_frame.pack_configure(padx=5, pady=5)
                main_frame.pack_propagate(False)


                label = ctk.CTkLabel(top_frame, width=80, height=20, text=weekday_name, fg_color="#444444", corner_radius=5)
                label.pack(side="left")

                label = ctk.CTkLabel(top_frame, width=20, height=20, text=day_enum, fg_color="#444444", corner_radius=5)
                label.pack(side="right")

                for j in range(len(rows)):
                    task_status = rows[j][2]
                    if j == 7:
                        frame = ctk.CTkFrame(main_frame)
                        frame.pack()
                        label = ctk.CTkLabel(frame, text="...", height=5, width=100, font=("", 15))
                        label.pack(side="top")
                        break
                    frame = ctk.CTkFrame(main_frame, height=30, width=230, fg_color="transparent")
                    frame.pack()
                    frame.pack_propagate(False)

                    item_label = ctk.CTkLabel(frame, text=rows[j][1], corner_radius=3, fg_color="#555555" if task_status=="pending" else "green", height=30, width=230, anchor="w", font=("", 10))
                    item_label.pack(side="left", padx=5, pady=5)

                if self.calendar.check_datetime_correspondency(self.this_week[i], self.real_today):
                    self.weekday_frame.configure(fg_color="#aaaaaa")
                    main_frame.bind("<Leave>", lambda event, color="#272727", index=i : on_leave(event, color, index))
                else:
                    main_frame.bind("<Leave>", lambda event, color="#272727", index=i: on_leave(event, color, index))

                btn = ctk.CTkButton(main_frame, text="view day", width=5, height=15)
                btn.bind("<Button-1>", command = lambda event, route_name="day_page", date=self.calendar.years[year_index][month_index][week_index][i] : self.redirect(event, route_name, date))
                btn.pack(side="bottom", pady=5)
                
        self.set_bottom_nav_frame()

        

class Month(Route):
    def __init__(self, name, calendar : Calendar, master, engine):
        super().__init__(name, master, engine)
        self.calendar = calendar


    @property
    def today(self):
        return self.calendar.get_today()
    
    @property
    def real_today(self):
        return self.calendar.get_today(real=True)


    def prev_month(self):
        self.calendar.update_index("month", amount=-1)
        self.master.render_page(self.name)
    

    def next_month(self):
        self.calendar.update_index("month", amount=1)
        self.master.render_page(self.name)


    def set_title_container(self):
        self.title_container = ctk.CTkFrame(self.main_frame, height=30)
        self.title_container.grid(row=0, column=0)


    def set_bottom_nav_frame(self):
        self.nav_bot = ctk.CTkFrame(self.master)
        self.nav_bot.grid(row=3, column=0, sticky="we")
        
        self.bot_btn_container = ctk.CTkFrame(self.nav_bot)
        self.bot_btn_container.pack()
        
        btn = ctk.CTkButton(self.bot_btn_container, text="<", command= lambda : self.prev_month())
        btn.pack(side="left")

        btn = ctk.CTkButton(self.bot_btn_container, text=">", command= lambda : self.next_month())
        btn.pack(side="left")


    def display(self):
        self.calendar.print_current_index()

        self.set_main_frame()
        self.set_title_container()

        year_index = self.calendar.year_index
        month_index = self.calendar.month_index

        def on_hover(event):
           event.widget.config(bg="white")
        
        def on_leave(event, color):
            event.widget.config(bg=color)

        months = self.calendar.get_this_month("weeks", offset=True)

        self.set_title_container()

        canvas = tk.Canvas(self.title_container, width=500, height=100)
        canvas.pack()
        canvas.create_text(250, 50, text="{}, {}".format(self.today.strftime("%B"), self.today.strftime("%Y")), font=("Helvetica 20 bold"))

        self.calendar_frame = ctk.CTkFrame(self.main_frame)
        self.calendar_frame.grid(row=1, column=0)

        index = 1

        for i in range(6):
            if i >= len(months[1]):
                for j in range(7):
                    frame = ctk.CTkFrame(self.calendar_frame)
                    frame.grid(row=i + 1, column=j)
                    canvas = tk.Canvas(frame, width=100, height=70 , highlightbackground="#444444", highlightthickness="1", bg="#555555")
                    canvas.grid(row=0, column=0)
                    canvas.bind("<Enter>", on_hover)
                    canvas.bind("<Leave>", lambda event, color="#555555" : on_leave(event, color))
                    if self.calendar.check_exact_week(months[1][len(months[1]) - 1]):
                        canvas.create_text(10, 5, text=months[2][index - 1][j].strftime("%d"), anchor="nw")
                    else:
                        canvas.create_text(10, 5, text=months[2][index][j].strftime("%d"), anchor="nw")
                
                index += 1

            else:
                for j in range(7):
                    if i == 0:
                        frame = ctk.CTkFrame(self.calendar_frame)
                        frame.grid(row=0, column=j)
                        canvas = tk.Canvas(frame, width=100, height=20, highlightbackground="black", background="white")
                        canvas.grid(row=0, column=0)
                        canvas.create_text(50, 10, text=months[1][i][j].strftime("%a"), font=("helvetica 10 bold"))
                    frame = ctk.CTkFrame(self.calendar_frame)
                    frame.grid(row=i + 1, column=j)
                    canvas = tk.Canvas(frame, width=100, height=70 , highlightbackground="#444444", bg="gray", highlightthickness=1)
                    canvas.bind("<Enter>", on_hover)
                    if (i == 0 and int(months[1][i][j].strftime("%d")) > 7) or i == len(months[1]) - 1 and int(months[1][i][j].strftime("%d")) < 7:
                        canvas.configure(bg="#555555")
                        canvas.bind("<Leave>", lambda event, color="#555555" : on_leave(event, color))
                    else:
                        canvas.bind("<Button-1>", lambda event, route_name="day_page", date=self.calendar.years[year_index][month_index][i][j] : self.redirect(event, route_name, date))
                        canvas.bind("<Leave>",  lambda event, color="gray" : on_leave(event, color))
                    if self.calendar.check_datetime_correspondency(months[1][i][j], self.real_today):
                        canvas.configure(bg="#cccccc")
                        canvas.bind("<Leave>", lambda event, color="#cccccc" : on_leave(event, color))
                    canvas.grid(row=0, column=0)
                    canvas.create_text(10, 5, text=months[1][i][j].strftime("%d"), anchor="nw")

            
        self.set_bottom_nav_frame()
