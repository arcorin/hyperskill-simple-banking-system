# Project: Simple Banking System
# https://hyperskill.org/projects/109
# Stage 1/4: Card anatomy
# Stage 2/4: Luhn algorithm
# Stage 3/4: I'm so lite
# Stage 4/4: Advanced system


import random
import sqlite3
from sqlite3 import Error


class Account:
    """ Create a card number with its pin and balance ...
        ... (including a method based on the Luhn Algorithm ...
        ... that calculates the check digit/check sum) """

    def __init__(self):

        # 1. Card anatomy:

        # Issuer Identification Number (IIN)
        self.issuer_id_number = str(400000)
        # Customer Account Number
        self.account_number = str(random.randint(0, 10 ** 9)).zfill(9)
        # Check digit / Checksum
        self.checksum = self.create_checksum_luhn_algorithm(self.issuer_id_number + self.account_number)

        # Card number
        self.card_number = self.issuer_id_number + self.account_number + self.checksum

        # 2. Card PIN
        self.pin = str(random.randint(0, 10 ** 4)).zfill(4)

        # 3. Card balance
        self.balance = 0

    def create_checksum_luhn_algorithm(self, number):
        """ Calculate and return the last 16th digit of the card number ...
            ... = checksum or check digit = the last digit of the card number) ...
            ... based on the first 15 digit of the card number using Luhn Algorithm"""

        # Luhn Algorithm:

        # Create a list with the first 15 digits of card number
        list_15 = [int(x) for x in number]

        # Step - Multiply odd digits by 2
        list_15_double_odds = [el * 2 if (n + 1) % 2 != 0 else el for n, el in enumerate(list_15)]

        # Step - Subtract 9 to numbers over 9
        list_15_minus_9 = [el - 9 if el > 9 else el for el in list_15_double_odds]

        # Step - Add all numbers and infer the check digit
        modulo = sum(list_15_minus_9) % 10
        last_digit = 10 - modulo if modulo != 0 else modulo

        return str(last_digit)


class BankingSystem:
    """ Create and update accounts """

    def __init__(self):
        self.logged_in = False
        self.sql_create_table_card = '''CREATE TABLE IF NOT EXISTS card (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        number TEXT UNIQUE,
                        pin TEXT,
                        balance INTEGER DEFAULT 0
                        );'''
        # save the card data for each session
        self.current_card_data = ()
        self.error_message = "\nWrong card number or PIN"
        self.choice_main_menu = ""
        self.choice_logged_menu = ""

    # method: create a Connection object that represents the database
    def create_connection(self, db_file):
        """ create a database connection to a SQLite database
            return: Connection object or None """
        conn = None
        try:
            conn = sqlite3.connect(db_file)
            return conn
        except Error as e:
            print(e)
        return conn

    # method: create table cards
    def create_table(self, conn, create_table_sql):
        """  create a table from the create_table_sql statement
             ... parameter conn = Connection object
             ... parameter create_table_sql = CREATE TABLE statement
             return:
        """
        try:
            # create a Cursor object and call its .execute() method to perform SQL queries
            c = conn.cursor()
            # execute SQL queries: create a table named card
            c.execute(create_table_sql)
        except Error as e:
            print(e)

    # method: create new account, return account data (card data)
    def create_account(self):
        # create new_account with class Account
        new_account = Account()

        print("\nYour card has been created")
        print(f"\nYour card number: \n{new_account.card_number}\nYour card PIN:\n{new_account.pin}")

        card_data = (new_account.card_number, new_account.pin, new_account.balance)
        return card_data

    # method: insert card data into table
    def insert_into_table(self, conn, card_data):
        sql = ''' INSERT INTO card(number, pin, balance)
        VALUES(?,?,?);'''

        # create a Cursor object
        c = conn.cursor()
        # execute sql query statement
        c.execute(sql, card_data)
        # commit the changes to the database
        conn.commit()

    # method: return a list of cards numbers
    def select_cards_numbers_from_table(self, conn):
        """ Select the column 'numbers' from card table ...
            ... Return a list of cards numbers """

        # list for all cards numbers
        cards = []

        # create a Cursor object
        c = conn.cursor()
        # execute SQL query statement
        c.execute("SELECT number FROM card")

        # return all rows of the response
        rows = c.fetchall()
        for row in rows:
            cards.append(row[0])
        return cards

    # method: select the user record from card table by card number
    def select_card_data_from_table(self, conn, number):
        """ Select from table the record where the number field = user card number
           ... Return a tuple containing card data (id, number, pin, balance) """

        # create a Cursor object
        c = conn.cursor()
        # execute SQL query statement
        c.execute("SELECT * FROM card WHERE number=?", (number,))

        # use .fetchone() method to get data returned by SQL query statement
        # return the first row of the response
        row = c.fetchone()
        return row

    # method: check card number and pin and log in user
    def log_in(self, conn):
        """ check card number and PIN:
            if they are valid the user logged in and the logged in menu is displayed...
            ....else the error message is displayed """

        user_card = input("\nEnter your card number:\n")

        cards = self.select_cards_numbers_from_table(conn)

        if user_card in cards:
            user_pin = input("Enter your PIN:\n")

            # save data card into class attribute self.current_card_data
            self.current_card_data = self.select_card_data_from_table(conn, user_card)

            # check if the user entered the correct pin
            if user_pin == self.current_card_data[2]:
                self.logged_in = True
                print("\nYou have successfully logged in!")
            # if the pin is not correct erase card data from the current card data attribute
            else:
                self.current_card_data = ()
                print(self.error_message)
        else:
            print(self.error_message)
        self.menus()

    # method: add income to balance
    def add_income(self, conn, data):
        """ Add income to current user row, balance column, in card table """
        sql = 'UPDATE card SET balance = balance + ? WHERE number = ?;'
        c = conn.cursor()
        c.execute(sql, data)
        conn.commit()
        print("Income was added!")
        self.menus()

    # method: transfer
    def transfer_amount(self, conn, data_subtract, data_add):
        """ Transfer money to another account of the data base """
        sql_subtract = 'UPDATE card SET balance = balance - ? WHERE number = ?;'
        sql_add = 'UPDATE card SET balance = balance + ? WHERE number = ?;'

        c = conn.cursor()
        c.execute(sql_subtract, data_subtract)
        conn.commit()

        c = conn.cursor()
        c.execute(sql_add, data_add)
        conn.commit()

        # print(f"amount {data_add[0]} was added to account {data_add[1]}")
        print("Success!")
        self.menus()

    # method: close account
    def close_account(self, conn, number):
        """ remove account from data base """
        sql = "DELETE FROM card WHERE number=?"
        c = conn.cursor()
        c.execute(sql, (number,))
        conn.commit()
        self.menus()

    # main method: display menus options and execute user choices
    def menus(self):
        """ 1. create database connection and create table
            2. menus + execution """

        database = 'card.s3db'

        # 1a. Create database connection
        conn = self.create_connection(database)

        # 1b. Create card table if does not exists
        if conn is not None:
            self.create_table(conn, self.sql_create_table_card)
            # print(table_list)
        else:
            print("Error! cannot create the database connection.")

        # print card table
        '''
        with conn:
            sql_select_all = 'SELECT * FROM card'
            c = conn.cursor()
            c.execute(sql_select_all)
            rows = c.fetchall()
            for row in rows:
                print(f"id: {row[0]}, number: {row[1]}, pin: {row[2]}, balance: {row[3]}")
        '''

        # 2. Menus
        # 2a. Menu when user is not logged in (start menu)
        if not self.logged_in:
            # display main menu and save user input
            self.choice_main_menu = input("\n1. Create an account\n2. Log into account\n0. Exit\n")

            # 1. Create an account and save account data into card_table
            if self.choice_main_menu == "1":
                # create account and save account data in card_data variable
                card_data = self.create_account()

                # insert card_data into card table in database
                with conn:
                    self.insert_into_table(conn, card_data)

            # 2. Log in
            elif self.choice_main_menu == "2":
                with conn:
                    self.log_in(conn)
            # 0. Exit
            elif self.choice_main_menu == "0":
                print("\nBye!")
                exit()
            else:
                self.menus()

        # 2b. Menu when user is logged in
        else:
            user_card = self.current_card_data[1]
            self.choice_logged_menu = input("""\n1. Balance
2. Add income
3. Do transfer
4. Close account 
5. Log out
0. Exit\n""")

            # 1. Balance
            if self.choice_logged_menu == "1":
                balance = self.select_card_data_from_table(conn, user_card)[3]
                with conn:
                    print(f"\nBalance: {balance}")
                self.menus()
            # 2. Add income
            elif self.choice_logged_menu == "2":
                income = int(input("Enter income:\n"))
                with conn:
                    self.add_income(conn, (income, user_card))
            # 3. Do transfer
            elif self.choice_logged_menu == "3":
                print("Transfer")
                destination_card = input("Enter card number:\n")
                cards = self.select_cards_numbers_from_table(conn)
                check_destination_account = Account()
                check_number = check_destination_account.create_checksum_luhn_algorithm(destination_card[:15])
                # print(check_number)
                # print(destination_card[-1])

                # if the destination card does not pass the Luhn algorithm
                if len(destination_card) != 16 or check_number != destination_card[-1]:
                    print("Probably you made a mistake in the card number. Please try again!")
                # else if the destination card is not valid - not in the cards list
                elif destination_card not in cards:
                    print("Such a card does not exist.")
                # do transfer if the destination card is valid
                else:
                    amount = int(input("Enter how much money you want to transfer:\n"))
                    with conn:
                        # get user balance from card table
                        user_balance = self.select_card_data_from_table(conn, user_card)[3]
                        if user_balance < amount:
                            print("Not enough money!")
                        # if there are enough money in the account
                        else:
                            with conn:
                                # transfer the amount from user account to destination account
                                self.transfer_amount(conn, (amount, user_card), (amount, destination_card))
                self.menus()

            # 4. Close account
            elif self.choice_logged_menu == "4":
                with conn:
                    self.close_account(conn, self.current_card_data[1])
                print("The account has been closed!")
            # 5. Log out
            elif self.choice_logged_menu == "5":
                self.current_card_data = ()
                self.logged_in = False
                print("\nYou have successfully logged out!")
                self.menus()
            # 0. Exit
            elif self.choice_logged_menu == "0":
                print("\nBye!")
                exit()
            else:
                self.menus()

        # in the end of the menus sessions set the variables to default ""
        self.choice_main_menu = ""
        self.choice_logged_menu = ""
        self.current_card_data = {}
        self.menus()


# method .seed() necessary for random.randint()
random.seed()

# First step of the program: initiate a new Session and start its .menus() method
session = BankingSystem()
session.menus()
