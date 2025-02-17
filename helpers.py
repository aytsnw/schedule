import customtkinter as ctk
from schedule_calendar import Calendar

ctk.set_appearance_mode("dark")



class App(ctk.CTk):
    

    """Root Window."""
    def __init__(self):
        super().__init__()
        self.DAY_X, self.DAY_Y=900, 700
        self.WEEK_X, self.WEEK_Y=1450, 500
        self.MONTH_X, self.MONTH_Y=900, 700

        self.default_coordinates = self.get_screen_center()
        self.default_resolution = [self.DAY_X, self.DAY_Y]
        self.init = True
        self.current_route =None
        self.geometry("{}x{}+{}+{}".format(self.default_resolution[0], self.default_resolution[1], self.default_coordinates[0], self.default_coordinates[1]))
        self.title("Schedule")
        self.protocol("WM_DELETE_WINDOW", self.end_children)
        self.grid_columnconfigure(0, weight=1)
        self.routes = {}
        self.windows = {}

    def end_children(self):
        children = self.windows.values()
        for child in children:
            child.destroy()
        self.destroy()


    def get_screen_center(self) -> list:
        """Returns the center cordinates of current screen."""
        width = self.winfo_screenwidth()
        height = self.winfo_screenheight()

        x = round(width/2 - 450)
        y = round(height/2 - 350)
        return [x, y]


    def add_route(self, route):
        """Passes route objects to the App object (self)."""
        self.routes[route.name] = route

    def add_window(self, window):
        """Passes window objects to the App object (self)."""
        self.windows[window.name] = window


    def set_init_state(self, state):
        """Defines if main window is being rendered via first initialization or via method: 'change_window_size'."""
        self.init = state


    def update_current_route(self, route_name : str):
        """Defines current route being displayed."""
        self.current_route = self.routes[route_name]


    def fill_header(self, header):
        label = ctk.CTkLabel(header, width=300, height=50, text="Schedule", font=("<family-name>", 35))
        label.pack()


    def set_header(self):
        """Displays top header with title/logo."""
        header = ctk.CTkFrame(self, fg_color="transparent", height=50)
        header.grid(row=0, column=0)
        header.pack_propagate(False)
        self.fill_header(header)


    def set_top_nav_frame(self):

        nav_top = ctk.CTkFrame(self, height=50, width=500)
        nav_top.grid(row=1, column=0, pady=10)

        frame = ctk.CTkFrame(nav_top, width=10)
        frame.pack(side="left", ipadx=1)
        

        self.btn_month = ctk.CTkButton(frame, text="Month")
        self.btn_month.configure(command= lambda route_name="month_page", reset_index=True : self.render_page(route_name, reset_index))
        self.btn_month.pack()

        frame = ctk.CTkFrame(nav_top)
        frame.pack(side="left", ipadx=1)

        self.btn_week = ctk.CTkButton(frame, text="Week")
        self.btn_week.configure(command= lambda route_name="week_page", reset_index=True : self.render_page(route_name, reset_index))
        self.btn_week.pack()

        frame = ctk.CTkFrame(nav_top)
        frame.pack(side="left", ipadx=1)

        self.btn_day = ctk.CTkButton(frame, text="Day")
        self.btn_day.configure(command= lambda route_name="day_page", reset_index=True : self.render_page(route_name, reset_index))
        self.btn_day.pack()
    

    def change_button_state(self, btn_name : str):
        if btn_name == "day":
            self.btn_day.configure(fg_color="white", text_color="black")
        elif btn_name == "week":
            self.btn_week.configure(fg_color="white", text_color="black")
        else:
            self.btn_month.configure(fg_color="white", text_color="black")
    

    def change_window_size(self, format="day"):
        current_x = self.winfo_x()
        current_y = self.winfo_y()
        print(current_x)
        print(current_y)
        day_x_adjustment = (self.WEEK_X - self.DAY_X)// 2
        month_x_adjustment = (self.WEEK_X - self.MONTH_X)// 2

        #check if route was triggered by app's initialization in order to keep default windows coordinates when booting up
        if not self.init:
            if format == "day":
                if self.current_route == self.routes["week_page"]:
                    self.geometry("{}x{}+{}+{}".format(self.DAY_X, self.DAY_Y, current_x + day_x_adjustment, current_y))
                else:
                    self.geometry("{}x{}+{}+{}".format(self.DAY_X, self.DAY_Y, current_x, current_y))

            elif format == "week":
                if not self.current_route == self.routes["week_page"]:
                    self.geometry("{}x{}+{}+{}".format(self.WEEK_X, self.WEEK_Y, current_x - day_x_adjustment, current_y))
                else:
                    self.geometry("{}x{}+{}+{}".format(self.WEEK_X, self.WEEK_Y, current_x, current_y))
            elif format == "month":
                if self.current_route == self.routes["week_page"]:
                    self.geometry("{}x{}+{}+{}".format(self.MONTH_X, self.MONTH_Y, current_x + month_x_adjustment, current_y))
                else:
                    self.geometry("{}x{}+{}+{}".format(self.MONTH_X, self.MONTH_Y, current_x, current_y))
        else:
            return


    def render_month_page(self):
        self.change_window_size(format="month")
        self.update_current_route("month_page")
        self.routes["month_page"].display()

    
    def render_week_page(self):
        self.change_window_size(format="week")
        self.update_current_route("week_page")
        self.routes["week_page"].display()


    def render_day_page(self, **kwargs):
        self.change_window_size(format="day")
        self.update_current_route("day_page")
        self.routes["day_page"].display(message=kwargs.get("message"))


    def render_page(self, route_name : str, reset_index : bool=False, message=None):

        print("rendering page...")
        children = self.winfo_children()
        for child in children:
            child.destroy()

        self.set_header()
        self.set_top_nav_frame()
        
        if route_name == "day_page":
            print("rendering day page...")
            if reset_index:
                self.routes["day_page"].calendar.set_index()
            self.change_button_state("day")
            self.render_day_page(message=message)
        elif route_name == "week_page":
            print("rendering week page...")
            if reset_index:
                self.routes["week_page"].calendar.set_index()
            self.change_button_state("week")
            self.render_week_page()
        elif route_name == "month_page":
            print("rendering month page...")
            if reset_index:
                self.routes["month_page"].calendar.set_index()
            self.change_button_state("month")
            self.render_month_page()
        else:
            raise("bad route, try: 'day' | 'week' | 'month'")
        



