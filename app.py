from schedule_calendar import Calendar
from sqlalchemy import create_engine, text
from helpers import App
from schedule_routes import Route, Day, Week, Month
from queries import create_table_tasks, create_table_recurrencies, create_table_both

calendar = Calendar()
recurrency_cal = Calendar()

engine = create_engine("sqlite:///schedule.db", echo=True)

engine = engine.connect()
engine.execute(text(create_table_tasks))
engine.execute(text(create_table_recurrencies))
engine.execute(text(create_table_both))
engine.commit()

app = App()

day_page = Day("day_page", calendar, app, recurrency_cal, engine)
month_page = Month("month_page", calendar, app, engine)
week_page = Week("week_page", calendar, app, engine)


app.add_route(month_page)
app.add_route(week_page)
app.add_route(day_page)



def main():
    app.render_page("day_page")
    app.set_init_state(False)
    app.mainloop()


if __name__ == "__main__":
    main()
    

    