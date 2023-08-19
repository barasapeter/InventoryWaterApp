# Import MySQL connector
import mysql.connector
import quick_variables

cnx = mysql.connector.connect(
    host="localhost",
    user="root",  # Replace this with your username
    password="quantumsoft",  # Replace this with your password
)

cursor = cnx.cursor()

cursor.execute("CREATE DATABASE IF NOT EXISTS TheosWaters")
cursor.execute("USE TheosWaters")
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS orders 
    (`NO` INT AUTO_INCREMENT PRIMARY KEY, 
    `customer` VARCHAR(200), 
    `merchant` VARCHAR(200), 
    `bottle NO` VARCHAR(200), 
    `description` VARCHAR(200), 
    `price` DECIMAL(10, 2), 
    `date of order` DATE, 
    `time of order` VARCHAR(20), 
    `status` VARCHAR(50), 
    `delivery date` DATE, 
    `time of delivery` VARCHAR(20))"""
)
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS customers (
	username VARCHAR(200) PRIMARY KEY,
    password VARCHAR(100),
    balance DECIMAL(10, 2),
    notifications INT
);"""
)
cursor.execute(
    """CREATE TABLE IF NOT EXISTS merchants (
	username VARCHAR(200) PRIMARY KEY,
    password VARCHAR(100)
);"""
)


def login_success(username, password):
    """Authenticate username and password"""
    merchants_create_table_query = """CREATE TABLE IF NOT EXISTS `merchants` (username VARCHAR(200) PRIMARY KEY, password VARCHAR(100));"""
    cursor.execute(merchants_create_table_query)
    cursor.execute(merchants_create_table_query.replace("merchants", "customers"))
    cnx.commit()
    merchant_authenticator_query = f'SELECT * FROM merchants WHERE username = "{username}" AND password = "{password}"'

    cursor.execute(merchant_authenticator_query)
    if cursor.fetchone():
        return {"is_successful": True, "user_type": "merchant"}

    cursor.execute(merchant_authenticator_query.replace("merchants", "customers"))
    if cursor.fetchone():
        return {"is_successful": True, "user_type": "customer"}

    return {"is_successful": False, "user_type": "unknown"}


def fetch_merchant_usernames():
    """Fetch a list of all merchants"""
    cursor.execute("SELECT username FROM MERCHANTS")
    return [i[0] for i in cursor.fetchall()]


def update_value(table_name, fieldname, newvalue, column_name, key):
    update_query = f'''UPDATE {table_name} SET `{fieldname}` = "{newvalue}" WHERE `{column_name}` = "{key}"'''
    cursor.execute(update_query)
    return "Record updated successfully!"


def fetch_customers() -> list:
    """Fetch the customers details and return a list of tuples of each table database row"""
    cursor.execute("SELECT username FROM customers")
    return [i[0] for i in cursor.fetchall()]


def fetch_customer_balance(customer_name):
    cursor.execute(f'SELECT balance FROM customers WHERE username = "{customer_name}"')
    return cursor.fetchall()[0][0]


def fetch_customer_notifications(customer_name) -> int:
    cursor.execute(
        f'SELECT notifications FROM customers WHERE username = "{customer_name}"'
    )
    return cursor.fetchall()[0][0]


def cfetch_orders(customer_username):
    """Fetch orders on a customer's perspective"""
    fetcher_query = f'''SELECT * FROM orders WHERE customer = "{customer_username}"'''
    cursor.execute(fetcher_query)
    return cursor.fetchall()


def fetch_orders(merchant_username):
    """Fetch orders on a merchant's perspective"""
    fetcher_query = f'''SELECT * FROM orders WHERE merchant = "{merchant_username}"'''
    cursor.execute(fetcher_query)
    return cursor.fetchall()


def fetch_bottles(merchant_username):
    """Fetches bottles of a merchat"""
    create_table_query = f"""CREATE TABLE IF NOT EXISTS {merchant_username}_bottles (`NO` INT AUTO_INCREMENT PRIMARY KEY, `Bottle size` INT, `Measurement unit` VARCHAR(100), `Cost` DECIMAL(10, 2));"""
    cursor.execute(create_table_query)
    fetch_bottles_query = f"SELECT * FROM {merchant_username}_bottles"
    cursor.execute(fetch_bottles_query)
    return cursor.fetchall()


def add_bottle(
    merchant_username, serial_number: str, bottle_size: str, measurement_unit, cost: str
):
    """Add new bottle to the database"""
    # Check if the bottles table for the logged in user exists
    create_table_query = f"""CREATE TABLE IF NOT EXISTS {merchant_username}_bottles (`NO` INT AUTO_INCREMENT PRIMARY KEY, `Bottle size` INT, `Measurement unit` VARCHAR(100), `Cost` DECIMAL(10, 2));"""
    cursor.execute(create_table_query)
    cnx.commit()
    try:
        if serial_number:
            insert_query = f'INSERT INTO {merchant_username}_bottles VALUES ("{serial_number}", "{bottle_size}", "{measurement_unit}", "{cost}")'
        else:
            insert_query = f'INSERT INTO {merchant_username}_bottles (`Bottle size`, `Measurement unit`, `Cost`) VALUES ("{bottle_size}", "{measurement_unit}", "{cost}")'
        try:
            cursor.execute(insert_query)
            return "Record has been added successfully!"
        except mysql.connector.errors.IntegrityError:
            return f'The serial number "{serial_number}" already exists. Please enter another one. Use auto Increment instead? Leave the SN entry blank to use auto increment.'
    except mysql.connector.errors.DatabaseError:
        return 'You have entered an invalid data type(s). Use numbers for "Serial NO", "Bottle size" and "Cost"'


def delete_bottle(merchant_username, bottle_serial_number):
    delete_query = (
        f"DELETE FROM {merchant_username}_bottles WHERE `NO` = {bottle_serial_number}"
    )
    try:
        cursor.execute(delete_query)
        return f"Record {bottle_serial_number} has been deleted successfully"
    except mysql.connector.errors.ProgrammingError:
        return f'Record deletion failed! We cannot find record "{bottle_serial_number}" anywhere in your database'


def dispense(merchant_username, bottle_serial_number, cost):
    """Record dispense data"""
    fetch_bottle_query = f'SELECT * FROM {merchant_username}_bottles WHERE `NO` = "{bottle_serial_number}"'
    cursor.execute(fetch_bottle_query)

    results = []
    for i in cursor.fetchall():
        results.append(i)

    try:
        float(cost)
    except:
        return "Failed! Please enter a numeric value for cost"

    if results:
        date_today = quick_variables.CustomCalendar.date_today()
        day_today = quick_variables.CustomCalendar.day_name_today()
        time_now = quick_variables.CustomCalendar.time_now()
        create_stats_table_query = f"""CREATE TABLE IF NOT EXISTS {merchant_username}_sales (`Sale number` INT AUTO_INCREMENT PRIMARY KEY, `Bottle Description` VARCHAR(50), `Cost` DECIMAL(10, 2), `Date of transaction` DATE, `Day` VARCHAR(20), `Time` VARCHAR(20))"""
        create_stats_query = f"""INSERT INTO {merchant_username}_sales (`Bottle Description`, `Cost`, `Date of transaction`, `Day`, `Time`) VALUES ("{results[0][1]} {results[0][2]}", {cost}, "{date_today}", "{day_today}", "{time_now}")"""
        cursor.execute(create_stats_table_query), cursor.execute(create_stats_query)
        return f"This will dispense {results[0][1]} {results[0][2]} of water. Would you like to proceed?"

    return f'We could not find bottle with serial "{bottle_serial_number}" anywhere in your database'


def fetch_sales(merchant_username):
    """Fetch sales stats"""
    create_stats_table_query = f"""CREATE TABLE IF NOT EXISTS {merchant_username}_sales (`Sale number` INT AUTO_INCREMENT PRIMARY KEY, `Bottle Description` VARCHAR(50), `Cost` DECIMAL(10, 2), `Date of transaction` DATE, `Day` VARCHAR(20), `Time` VARCHAR(20))"""
    cursor.execute(create_stats_table_query)
    cnx.commit()
    fetch_sales_stats_query = f"SELECT * FROM {merchant_username}_sales"
    cursor.execute(fetch_sales_stats_query)
    return cursor.fetchall()


def place_order(customer_username, merchant_username, item: tuple):
    """Places an order"""
    create_orders_table_query = "CREATE TABLE IF NOT EXISTS orders (`NO` INT AUTO_INCREMENT PRIMARY KEY, `customer` VARCHAR(200), merchant VARCHAR(200), `bottle NO` VARCHAR(200), `description` VARCHAR(200), `price` DECIMAL(10, 2), `date of order` DATE, `time of order` VARCHAR(20), `status` VARCHAR(50), `delivery date` DATE, `time of delivery` VARCHAR(20))"
    cursor.execute(create_orders_table_query)
    cnx.commit()

    customer_is_valid = None
    merchant_is_valid = None

    if customer_username in fetch_customers():
        customer_is_valid = True

    if merchant_username in fetch_merchant_usernames():
        merchant_is_valid = True

    if customer_is_valid and merchant_is_valid:
        insert_query = f"""
        INSERT INTO orders (`customer`, `merchant`, `bottle NO`, `description`, `price`, `date of order`, `time of order`, `status`, `delivery date`, `time of delivery`) 
        VALUES 
            ("{customer_username}", "{merchant_username}", "{item[0]}", "{item[1]} {item[2]}", {item[3]}, "{quick_variables.CustomCalendar.date_today()}", "{quick_variables.CustomCalendar.time_now()}", "pending", NULL, NULL)"""
        cursor.execute(insert_query)

        return "Order placed successfully! Please wait for the merchant to respond."

    return "Invalid merchant or customer"


def fill_order(order_id):
    """Change the status from "pending" to "filled". This also goes for delivery date and delivery time."""
    update_value("orders", "status", "delivered", "NO", order_id)
    update_value(
        "orders",
        "delivery date",
        quick_variables.CustomCalendar.date_today(),
        "NO",
        order_id,
    )
    update_value(
        "orders",
        "time of delivery",
        quick_variables.CustomCalendar.time_now(),
        "NO",
        order_id,
    )
    return "done"


def cache_order(order_id):
    cache_query = """
    CREATE TABLE IF NOT EXISTS cached_orders 
        (`NO` INT PRIMARY KEY, 
        `customer` VARCHAR(200), 
        `merchant` VARCHAR(200), 
        `bottle NO` VARCHAR(200), 
        `description` VARCHAR(200), 
        `price` DECIMAL(10, 2), 
        `date of order` DATE, 
        `time of order` VARCHAR(20), 
        `status` VARCHAR(50), 
        `delivery date` DATE, 
        `time of delivery` VARCHAR(20))"""
    cursor.execute(cache_query)
    cursor.execute(f"SELECT * FROM orders WHERE `NO` = {order_id}")
    row = cursor.fetchone()

    # Insert the fetched row into the cached_orders table
    insert_query = """
        INSERT INTO cached_orders
        (`NO`, `customer`, `merchant`, `bottle NO`, `description`, `price`, `date of order`, `time of order`, `status`, `delivery date`, `time of delivery`)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(insert_query, row)

    return "done"


def fetch_cached_orders(customer_name):
    cursor.execute(
        f'''SELECT * FROM cached_orders WHERE customer = "{customer_name}"'''
    )
    return cursor.fetchall()


def delete_cached_orders(customer_name):
    """Delete the cached product if the notification has been viewed."""
    cursor.execute(f'''DELETE FROM cached_orders WHERE customer = "{customer_name}"''')
    update_value("customers", "notifications", 0, "username", customer_name)
    cnx.commit()
    return "done"


def add_user(user_type, username, password):
    """Adds either a new merchant or a new customer to the database."""
    if user_type == "merchant":
        add_query = f'INSERT INTO merchants VALUES ("{username}", "{password}")'
    else:
        add_query = f'INSERT INTO customers VALUES ("{username}", "{password}", 2500, 0)'  # Every new customer is given an initial token of Kshs2500. Pay me more and I advance this functionality 🙂
    cursor.execute(add_query)
    cnx.commit()
    return "Account created successfully."


# For tsting purposes
if __name__ == "__main__":
    import pprint

    print(add_user("customer", "barasa", "barasa123"))
    cnx.commit()
    cnx.close()
