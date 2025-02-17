create_table_tasks = "CREATE TABLE IF NOT EXISTS tasks (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, task TEXT, description TEXT, recurrent TEXT NOT NULL, recurrency_type TEXT, recurrency_amount INT, status TEXT DEFAULT 'pending', day INTEGER, month INTEGER, year INTEGER)"
create_table_both = "CREATE TABLE IF NOT EXISTS tasks_recurrencies (task_id INTEGER, recurrency_id INTEGER)"
create_table_recurrencies =  "CREATE TABLE IF NOT EXISTS recurrencies (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT)"
