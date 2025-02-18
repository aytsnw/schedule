from datetime import datetime
from calendar import Calendar as CalendarImport

class Calendar(CalendarImport):

    def __init__(self, **kwargs):
        super().__init__(firstweekday=0)
        self.year_index_limit = 9
        self.years = []
        self.parse_data()
        self.set_index()


    def parse_data(self):
        for i in range(self.year_index_limit + 1):
            start = 2025
            self.years.append([month for quarter in self.yeardatescalendar(start + i, 1) for month in quarter])


    def set_index(self, custom_date : datetime=None):
        """Set calendar indices."""
        #Try to implement binary search to find the match instead of nested for loops.
        if not custom_date:
            now = datetime.now()
            for year_index, year in enumerate(self.years):
                for month in year:
                    for week in month:
                        for day_index, day in enumerate(week):
                            if day.strftime("%d") == now.strftime("%d") and day.strftime("%B") == now.strftime("%B") and day.strftime("%Y") == now.strftime("%Y"):
                                self.day_index = int(day_index)
                                self.year_index = int(year_index)
                                self.month_index = int(now.strftime("%m")) - 1
                                for index, week in enumerate(self.years[self.year_index][self.month_index]):
                                    for day in week:
                                        if day.strftime("%d") == now.strftime("%d") and day.strftime("%B") == now.strftime("%B") and day.strftime("%Y") == now.strftime("%Y"):
                                            self.week_index = int(index)
                                            return
        else:
            now = custom_date
            for year_index, year in enumerate(self.years):
                for month in year:
                    for week in month:
                        for day_index, day in enumerate(week):
                            if day.strftime("%d") == now.strftime("%d") and day.strftime("%B") == now.strftime("%B") and day.strftime("%Y") == now.strftime("%Y"):
                                self.day_index = int(day_index)
                                self.year_index = int(year_index)
                                self.month_index = int(now.strftime("%m")) - 1
                                print(self.month_index)
                                for index, week in enumerate(self.years[self.year_index][self.month_index]):
                                    for day in week:
                                        if day.strftime("%d") == now.strftime("%d") and day.strftime("%B") == now.strftime("%B") and day.strftime("%Y") == now.strftime("%Y"):
                                            self.week_index = int(index)
                                            return



    def check_exact_week(self, week : list) -> bool:
        if int(week[1].strftime("%d")) < int(week[0].strftime("%d")):
            return False

        for i in range(len(week[2:])):
            i += 2
            if int(week[i].strftime("%d")) < int(week[i-1].strftime("%d")):
                return False
        
        return True
    

    def find_first_monthday(self, month_index : int):
        month = self.years[self.year_index][month_index]
        for week_index, week in enumerate(month):
            for day_index, day in enumerate(week):
                if day.strftime("%d") == "01":
                    return [week_index, day_index]
                
                
    def print_current_index(self):
        print ("Year index: {}, Month index: {}, Week index: {}, Day index: {}.".format(self.year_index, self.month_index, self.week_index, self.day_index))


    def update_index(self, index : str, amount: int = 0, **kwargs) -> bool:

        if index == "year":
            if kwargs.get("set") == None:
                if self.year_index + amount > self.year_index_limit or self.year_index + amount < 0:
                    print("Year index out of bounds.")
                    return False
                else:
                    self.year_index += amount
                    if self.update_index("month", set=0):
                        return True
                    return False
            else:
                try:
                    self.year_index = kwargs["set"]
                    self.update_index("month", set=0)
                    return True
                except IndexError:
                    print("Year index out of bounds")
                    return False

        if index == "month":
            if kwargs.get("set") == None:
                if self.month_index + amount > 11:
                    if self.update_index("year", amount=1):
                        self.month_index = 0
                        self.update_index("week", set=self.find_first_monthday(self.month_index)[0])
                        return True
                    return False
                elif self.month_index + amount < 0:
                    if self.update_index("year", amount=-1):
                        self.month_index = 11
                        self.update_index("week", set=self.find_first_monthday(self.month_index)[0])
                        return True
                    return False
                else:
                    self.month_index += amount
                    self.update_index("week", set=self.find_first_monthday(self.month_index)[0])
                    return True
            else:
                try:
                    self.month_index = kwargs["set"]
                    self.update_index("week", set=self.find_first_monthday(self.month_index)[0])
                    return True
                except IndexError:
                    print("Month index out of bounds")
                    return False

        if index == "week":
            #print("week triggered")
            #here it is necessary to skip 1 more week when the index is in the edges because of the way the data has been parsed:
            #the first and last week of each month share the same data when they are not exactly seven days of the given month
            if kwargs.get("set") == None:
                if self.week_index + amount > len(self.years[self.year_index][self.month_index]) - 1:
                    self.update_index("month", amount=1)
                    week = self.years[self.year_index][self.month_index][self.week_index]
                    if self.check_exact_week(week):
                        self.week_index = 0
                    else:
                        self.week_index = 1
                    self.update_index("day", set=self.find_first_monthday(self.month_index)[1])
                    return True
                elif self.week_index + amount < 0:
                    self.update_index("month", amount=-1)
                    week = self.years[self.year_index][self.month_index][self.week_index]
                    if self.check_exact_week(week):
                        self.week_index = len(self.years[self.year_index][self.month_index]) - 1
                        return True
                    else:
                        self.week_index = len(self.years[self.year_index][self.month_index]) - 2
                        return True
                else:
                    self.week_index += amount
                    self.day_index = 0
                    return True
            else:
                try:
                    self.week_index = kwargs["set"]
                    self.update_index("day", set=self.find_first_monthday(self.month_index)[1])
                    return True
                except IndexError:
                    print("Week index out of bounds")
                    return False

        if index == "day":
            if kwargs.get("set") == None:
                if self.day_index + amount > 6:
                    self.update_index("week", amount=1)
                    self.day_index = 0
                    return True
                elif self.day_index + amount < 0:
                    self.update_index("week", amount=-1)
                    self.day_index = 6
                    return True
                else:
                    self.day_index += amount
                    return True
            else:
                try:
                    self.day_index = kwargs["set"]
                except IndexError:
                    print("Day index out of bounds")
                    return False



    def get_today(self, real=False) -> datetime:
        if not real:
            today = self.years[self.year_index][self.month_index][self.week_index][self.day_index]
        else: 
            today = datetime.now()
        return today


    def get_this_week(self, mode="days") -> list | int:
        """Returns a list of datetime objects of current index week, or the current week index within the month."""
        if mode == "days":
            this_week = self.years[self.year_index][self.month_index][self.week_index]
            return this_week

        elif mode == "index":
            for index, week in enumerate(self.years[self.year_index][self.month_index]):
                for day in week:
                    if day == self.get_today():
                        return index
                    
    def get_this_month(self, mode="weeks", offset=None) -> list | int:
        year_index = self.year_index
        month_index = self.month_index
        week_index = self.week_index
        day_index = self.day_index

        if mode == "weeks":
            this_month = self.years[self.year_index][self.month_index]
            if offset:
                self.update_index("month", amount=1)
                next_month = self.years[self.year_index][self.month_index]
                self.update_index("month", amount=-1)
                prev_month = self.years[self.year_index][self.month_index]
                self.update_index("year", set=year_index)
                self.update_index("month", set=month_index)
                self.update_index("week", set=week_index)
                self.update_index("day", set=day_index)
                return [prev_month, this_month, next_month]
            
            return this_month
        
        elif mode == "index":
            for index, month in enumerate(self.years[self.year_index]):
                for week in month:
                    for day in week:
                        if day == self.get_today():
                            return index

    
    def next(self, index : str = "month"):
        if index:
            self.update_index(index, amount=1)
    

    def prev(self, index : str = "month"):
        if index:
            self.update_index(index, amount=-1)

    def check_datetime_correspondency(self, datetime_1 : datetime, datetime_2 : datetime):
        if datetime_1.strftime("%d") == datetime_2.strftime("%d") and datetime_1.strftime("%m") == datetime_2.strftime("%m") and datetime_1.strftime("%Y") == datetime_2.strftime("%Y"):
            return True
        return False
