import sqlite3

def display_database_content(db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    if not tables:
        print("No tables found in the database.")
    else:
        print(f"\n📂 Database: {db_file}")
        print("=======================================")

        for table in tables:
            table_name = table[0]
            print(f"\n🗂 TABLE: {table_name}")
            print("---------------------------------------")

            # Get all rows from the table
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()

            # Get column names
            column_names = [description[0] for description in cursor.description]

            print(" | ".join(column_names))
            print("-" * 40)

            for row in rows:
                print(row)

    conn.close()

# 🔰 Run
display_database_content("database/dns_filter.db")   # <-- change database file name

# 🔚 Prevent program from closing
input("\nPress ENTER to exit...")
