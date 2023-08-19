# Import the required libraries
import os
import reports
import database
import quick_variables
import typing, random
from PIL import Image
import string
import shutil
import glob
import re

from tkinter import ttk
import customtkinter as ctk
from tkinter.filedialog import askdirectory
from tkinter.messagebox import *
from typing import Union


# App starts here..
class App(ctk.CTk):
    width = 900
    height = 600

    def cascade_bottledata(
        *args,
        merchant_username,
        cascade_bottledata_container,
        loggedin_customer,
        pricetagvar,
        showordersframe,
        orders_table,
    ):
        """Cascades bottle data. Traces when the user types the field and searches for corresponding data in the database."""
        cascade_bottledata_container.grid_forget()
        showordersframe.grid_forget()
        orders_table.grid_forget()
        if merchant_username in database.fetch_merchant_usernames():
            [
                widget.destroy()
                for widget in cascade_bottledata_container.winfo_children()
            ]
            cascade_bottledata_container.grid(row=0, column=0)
            bottles = database.fetch_bottles(merchant_username)
            bottle_records: dict[typing.Any] = {}
            for record in bottles:
                bottle_records[str(record[0])] = {
                    "bottle size": record[1],
                    "measurement unit": record[2],
                    "cost": record[3],
                }
            bottle_token_codes = list(bottle_records.keys())

            def autofill(sv):
                if sv in bottle_records.keys():
                    [
                        (i.configure(state="normal"), i.delete(0, "end"))
                        for i in [
                            refill_bottle_size_ent,
                            refill_bottle_unit_ent,
                            refill_bottle_cost_ent,
                        ]
                    ]
                    refill_bottle_size_ent.insert(0, bottle_records[sv]["bottle size"])
                    refill_bottle_unit_ent.insert(
                        0, bottle_records[sv]["measurement unit"]
                    )
                    refill_bottle_cost_ent.insert(0, bottle_records[sv]["cost"])
                    [
                        i.configure(state="disabled")
                        for i in [
                            refill_bottle_size_ent,
                            refill_bottle_unit_ent,
                            refill_bottle_cost_ent,
                        ]
                    ]
                else:
                    for i in [
                        refill_bottle_size_ent,
                        refill_bottle_unit_ent,
                        refill_bottle_cost_ent,
                    ]:
                        i.configure(state="normal")
                        i.delete(0, "end")
                        i.configure(state="disabled")

            def place_order():
                """Place order"""
                if (
                    refill_bottle_serialno_ent.get()
                    and refill_bottle_size_ent.get() != ""
                ):
                    response = database.place_order(
                        loggedin_customer,
                        merchant_username,
                        (
                            refill_bottle_serialno_ent.get(),
                            refill_bottle_size_ent.get(),
                            refill_bottle_unit_ent.get(),
                            refill_bottle_cost_ent.get(),
                        ),
                    )

                    # Check for balance before placing an order
                    customer_balance = float(
                        database.fetch_customer_balance(loggedin_customer)
                    )
                    if customer_balance >= float(refill_bottle_cost_ent.get()):
                        if askyesnocancel(
                            "TheosWaters",
                            f"This action will send an order to {merchant_username}. Would you like to proceed?",
                        ):
                            customer_balance -= float(refill_bottle_cost_ent.get())
                            pricetagvar.set(
                                f"Your balance is KES{customer_balance:.2f}"
                            )
                            database.update_value(
                                "customers",
                                "balance",
                                customer_balance,
                                "username",
                                loggedin_customer,
                            )
                            database.cnx.commit()
                            showinfo("TheosWaters", response)
                    else:
                        showwarning(
                            "TheosWaters",
                            f"Sorry, you do not have enough amount to place this order. Your balance is KES{customer_balance}, please top up to proceed.",
                        )
                else:
                    showwarning("TheosWaters", "Please select an item in the list!")

            global refill_bottle_size_ent, refill_bottle_unit_ent, refill_bottle_cost_ent

            sv = ctk.StringVar()
            sv.trace("w", lambda name, index, mode, sv=sv: autofill(sv.get()))

            ctk.CTkLabel(cascade_bottledata_container, text="Serial NO").grid(
                row=0, column=0, padx=5, pady=(20, 5)
            )
            refill_bottle_serialno_ent = ctk.CTkComboBox(
                cascade_bottledata_container,
                width=200,
                values=bottle_token_codes,
                variable=sv,
            )
            refill_bottle_serialno_ent.grid(row=0, column=1, padx=(0, 5), pady=(20, 5))
            refill_bottle_serialno_ent.set("")
            ctk.CTkLabel(cascade_bottledata_container, text="Bottle size").grid(
                row=1, column=0, padx=5, pady=(0, 5)
            )
            refill_bottle_size_ent = ctk.CTkEntry(
                cascade_bottledata_container, width=200
            )
            refill_bottle_size_ent.grid(row=1, column=1, padx=(0, 5), pady=(0, 5))
            ctk.CTkLabel(cascade_bottledata_container, text="Unit").grid(
                row=2, column=0, padx=5, pady=(0, 5)
            )
            refill_bottle_unit_ent = ctk.CTkEntry(
                cascade_bottledata_container, width=200
            )
            refill_bottle_unit_ent.grid(row=2, column=1, padx=(0, 5), pady=(0, 5))
            ctk.CTkLabel(cascade_bottledata_container, text="Cost").grid(
                row=3, column=0, padx=5, pady=(0, 5)
            )
            refill_bottle_cost_ent = ctk.CTkEntry(
                cascade_bottledata_container, width=200
            )
            refill_bottle_cost_ent.grid(row=3, column=1, padx=(0, 5), pady=(0, 5))
            refill_refill_button = ctk.CTkButton(
                cascade_bottledata_container,
                command=place_order,
                width=350,
                height=40,
                fg_color="#513E2B",
                hover_color="#1FADFF",
                border_color="#1FADFF",
                border_width=1,
                font=ctk.CTkFont("Rockwell Extra Bold", 16),
                text="ORDER NOW",
            )
            refill_refill_button.grid(
                row=4, column=0, columnspan=2, padx=5, pady=(20, 10), sticky="ew"
            )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loggedin_username = ctk.StringVar()
        self.latestreceiptvar = ctk.StringVar()

        # Set the window properties
        self.geometry(f"{self.width}x{self.height}")
        self.wm_attributes("-alpha", 0.95)
        self.resizable(False, False)
        self.title("Water management System")

        # Create a beautiful backgrund image for the main screen
        ctk.CTkLabel(
            self,
            text=None,
            image=ctk.CTkImage(
                Image.open("./images/background.jpg"), size=(self.width, self.height)
            ),
        ).grid(row=0, column=0, sticky="nwes")

        # Login form
        self.login_form = ctk.CTkFrame(self, border_width=1, border_color="green")
        self.login_form.grid(row=0, column=0, sticky="ns", pady=50)
        ctk.CTkLabel(
            self.login_form,
            text="WATER MANAGEMENT\nSYSTEM",
            font=ctk.CTkFont("Arial", 20, "bold", "roman"),
        ).grid(row=0, column=0, columnspan=2, padx=5, pady=(50, 50))
        ctk.CTkLabel(
            self.login_form,
            text=None,
            image=ctk.CTkImage(Image.open("./images/username_icon.png"), size=(30, 30)),
        ).grid(row=1, column=0, padx=1, pady=(0, 10))
        ctk.CTkLabel(
            self.login_form,
            text=None,
            image=ctk.CTkImage(Image.open("./images/lock.png"), size=(50, 30)),
        ).grid(row=2, column=0, padx=1, pady=(0, 10))

        # Username and password entry widgets
        self.user_name_entry = ctk.CTkEntry(
            self.login_form, width=200, placeholder_text="Username..."
        )
        self.user_name_entry.grid(row=1, column=1, padx=(0, 10))
        self.password_entry = ctk.CTkEntry(
            self.login_form, width=200, show="•", placeholder_text="Password..."
        )
        self.password_entry.grid(row=2, column=1, padx=(0, 10))

        # Customers dash
        self.customerdashboard = ctk.CTkFrame(self, corner_radius=50)
        ctk.CTkLabel(
            self.customerdashboard,
            text=None,
            image=ctk.CTkImage(Image.open("./images/glass_water.jpg"), size=(450, 600)),
            font=ctk.CTkFont("Arial", 18, "bold", "roman"),
        ).grid(row=0, column=0, sticky="nwse")
        self.welcome_message = ctk.CTkLabel(
            self.customerdashboard,
            corner_radius=15,
            font=ctk.CTkFont("Arial", 12, "bold", "roman"),
        )
        self.welcome_message.grid(row=0, column=0, padx=5, pady=5, sticky="new")

        self.customer_show_orders_frame = ctk.CTkFrame(self.customerdashboard)

        self.balancetag_variable = ctk.StringVar()
        self.customeraccbaltag = ctk.CTkButton(
            self.customerdashboard,
            width=180,
            corner_radius=3,
            font=ctk.CTkFont("consolas", 11, "normal", "roman"),
            textvariable=self.balancetag_variable,
            fg_color="#8126BF",
            hover_color="#BB4790",
        )
        self.customeraccbaltag.grid(row=0, column=0, padx=5, pady=(40, 0), sticky="nw")

        self.customerNotificationTracker = ctk.StringVar()
        self.orderstag = ctk.CTkButton(
            self.customerdashboard,
            width=180,
            corner_radius=3,
            font=ctk.CTkFont("consolas", 11, "normal", "roman"),
            textvariable=self.customerNotificationTracker,
            fg_color="#8126BF",
            hover_color="#BB4790",
            # hover_color='#1FADFF', fg_color='#513E2B',
            command=lambda: self.customer_view_orders(self.loggedin_username.get()),
        )
        self.orderstag.grid(row=0, column=0, padx=5, pady=(40, 0), sticky="ne")

        self.cascade_bottledata_container = ctk.CTkFrame(self.customerdashboard)
        svx = ctk.StringVar()
        self.merchant_username_ent = ctk.CTkComboBox(
            self.customerdashboard,
            variable=svx,
            justify="center",
            values=database.fetch_merchant_usernames(),
        )
        self.merchant_username_ent.grid(
            row=0, column=0, pady=(100, 5), padx=90, sticky="nwe"
        )
        self.merchant_username_ent.set("--Select--")
        svx.trace(
            "w",
            lambda name, index, mode, svx=svx: self.cascade_bottledata(
                merchant_username=self.merchant_username_ent.get(),
                cascade_bottledata_container=self.cascade_bottledata_container,
                loggedin_customer=self.loggedin_username.get(),
                pricetagvar=self.balancetag_variable,
                showordersframe=self.customer_show_orders_frame,
                orders_table=self.customer_show_orders_frame,
            ),
        )
        ctk.CTkButton(
            self.customerdashboard,
            anchor="w",
            border_spacing=10,
            corner_radius=3,
            hover_color=("gray70", "gray30"),
            fg_color="transparent",
            text="Log out?",
            image=ctk.CTkImage(Image.open("./images/logout.png")),
            compound="left",
            command=self.logoutcustomer,
        ).grid(row=0, column=0, pady=(0, 5), sticky="s")

        # Merchant dash
        self.merchant_dashboard = ctk.CTkFrame(self)
        self.leftsidebar = ctk.CTkFrame(self.merchant_dashboard)
        self.leftsidebar.pack(side="left", fill="y")
        self.mainbar = ctk.CTkFrame(self.merchant_dashboard)
        self.mainbar.pack()
        ctk.CTkLabel(
            self.mainbar,
            text=None,
            image=ctk.CTkImage(
                Image.open("./images/dash_background.jpg"),
                size=(self.width - 140, self.height),
            ),
        ).grid(row=0, column=0)
        self.dynamic_text = ctk.StringVar()
        self.dynamic_text.set("Home")
        self.tablabel = ctk.CTkLabel(
            self.mainbar,
            font=ctk.CTkFont(None, 24, "bold"),
            width=400,
            height=54,
            textvariable=self.dynamic_text,
        )
        self.tablabel.grid(row=0, column=0, sticky="nwe")
        self.open_dash_widgets: list[
            Union[ctk.CTkLabel, ctk.CTkFrame, ctk.CTkButton]
        ] = []

        self.downloadall = ctk.CTkButton(
            self.mainbar,
            command=lambda: self.download_receipts("all"),
            text="Download all receipts",
            image=ctk.CTkImage(Image.open("./images/multiple-downloads.png")),
            corner_radius=0,
            anchor="w",
            border_spacing=10,
            height=40,
            text_color="black",
            hover_color="#E9D5CD",
            fg_color="#FEF9C3",
        )
        self.download_button = ctk.CTkButton(
            self.mainbar,
            command=lambda: self.download_receipts("one"),
            text="Download last receipt",
            image=ctk.CTkImage(Image.open("./images/downloadico.png")),
            corner_radius=0,
            anchor="w",
            border_spacing=10,
            height=40,
            text_color="black",
            hover_color="#E9D5CD",
            fg_color="#FEF9C3",
        )

        def trace_serialno_input(text_container):
            for field in [
                self.bottle_size_ent,
                self.bottle_unit_ent,
                self.bottle_cost_ent,
            ]:
                field.delete(0, "end")
            if text_container.get() in bottle_records.keys():
                self.bottle_size_ent.insert(0, bottle_records[sv.get()]["bottle size"])
                self.bottle_unit_ent.insert(
                    0, bottle_records[sv.get()]["measurement unit"]
                )
                self.bottle_cost_ent.insert(0, bottle_records[sv.get()]["cost"])

        # Tabs start here...
        sv = ctk.StringVar()
        sv.trace("w", lambda name, index, mode, sv=sv: trace_serialno_input(sv))
        self.bottles_tab = ctk.CTkFrame(
            self.mainbar, corner_radius=5, border_width=1, border_color="green"
        )
        self.bottles_entry_frame = ctk.CTkFrame(self.bottles_tab)
        self.bottles_entry_frame.pack(expand="yes")
        ctk.CTkLabel(self.bottles_entry_frame, text="Serial NO").grid(
            row=0, column=0, padx=5
        )
        self.bottle_serialno_ent = ctk.CTkComboBox(
            self.bottles_entry_frame, variable=sv
        )
        self.bottle_serialno_ent.grid(row=0, column=1, pady=(10, 5))
        self.bottle_serialno_ent.set("")
        ctk.CTkLabel(self.bottles_entry_frame, text="Bottle size").grid(row=1, column=0)
        self.bottle_size_ent = ctk.CTkEntry(self.bottles_entry_frame)
        self.bottle_size_ent.grid(row=1, column=1, pady=(0, 5))
        ctk.CTkLabel(self.bottles_entry_frame, text="Unit").grid(
            row=2, column=0, padx=5
        )
        self.bottle_unit_ent = ctk.CTkEntry(self.bottles_entry_frame)
        self.bottle_unit_ent.grid(row=2, column=1, pady=(0, 5))
        ctk.CTkLabel(self.bottles_entry_frame, text="Cost").grid(
            row=3, column=0, padx=5
        )
        self.bottle_cost_ent = ctk.CTkEntry(self.bottles_entry_frame)
        self.bottle_cost_ent.grid(row=3, column=1, padx=5, pady=(0, 10))
        self.btns_frame = ctk.CTkFrame(self.bottles_tab)
        self.btns_frame.pack(pady=(0, 20))

        def save_bottle():
            response = database.add_bottle(
                self.loggedin_username.get(),
                self.bottle_serialno_ent.get(),
                self.bottle_size_ent.get(),
                self.bottle_unit_ent.get(),
                self.bottle_cost_ent.get(),
            )
            if "Record has been added successfully!" in response:
                if askyesnocancel(
                    "TheosWaters",
                    "This action will add a new record in the database. Are you sure you wat to proceed?",
                ):
                    database.cnx.commit()
                    self.bottles: list[tuple] = database.fetch_bottles(
                        self.loggedin_username.get()
                    )
                    global bottle_records
                    bottle_records = {}
                    for record in self.bottles:
                        bottle_records[str(record[0])] = {
                            "bottle size": record[1],
                            "measurement unit": record[2],
                            "cost": record[3],
                        }
                    bottle_serial_numbers = list(bottle_records.keys())
                    self.bottle_serialno_ent.configure(values=bottle_serial_numbers)
                    self.refill_bottle_serialno_ent.configure(
                        values=bottle_serial_numbers
                    )
                    showinfo("TheosWaters", response)
            else:
                showinfo("TheosWaters", response)

        def delete_bottle():
            response = database.delete_bottle(
                self.loggedin_username.get(), self.bottle_serialno_ent.get()
            )
            if "success" in response:
                if askyesnocancel(
                    "TheosWaters",
                    "You are about to delete a record. Are you sure you want to proceed?",
                ):
                    database.cnx.commit()
                    self.bottles: list[tuple] = database.fetch_bottles(
                        self.loggedin_username.get()
                    )
                    global bottle_records
                    bottle_records = {}
                    for record in self.bottles:
                        bottle_records[str(record[0])] = {
                            "bottle size": record[1],
                            "measurement unit": record[2],
                            "cost": record[3],
                        }
                    bottle_serial_numbers = list(bottle_records.keys())
                    self.bottle_serialno_ent.configure(values=bottle_serial_numbers)
                    self.refill_bottle_serialno_ent.configure(
                        values=bottle_serial_numbers
                    )
                    self.bottle_serialno_ent.set("")
                    for field in [
                        self.bottle_size_ent,
                        self.bottle_unit_ent,
                        self.bottle_cost_ent,
                    ]:
                        field.delete(0, "end")
                    showinfo("TheosWaters", response)
            else:
                showwarning("TheosWaters", response)

        self.save_bottle_button = ctk.CTkButton(
            self.btns_frame,
            hover_color="dark green",
            fg_color="transparent",
            border_width=3,
            height=40,
            text="SAVE",
            command=save_bottle,
        )
        self.save_bottle_button.pack(side="left", padx=(0, 5))
        self.save_bottle_button = ctk.CTkButton(
            self.btns_frame,
            hover_color="dark red",
            height=40,
            fg_color="transparent",
            border_width=3,
            text="DELETE",
            command=delete_bottle,
        )
        self.save_bottle_button.pack(side="right")

        def trace_refill_serial_ent(text_container):
            for field in [
                self.refill_bottle_size_ent,
                self.refill_bottle_unit_ent,
                self.refill_bottle_cost_ent,
            ]:
                field.delete(0, "end")
            if text_container.get() in bottle_records.keys():
                self.refill_bottle_size_ent.insert(
                    0, bottle_records[sv2.get()]["bottle size"]
                )
                self.refill_bottle_unit_ent.insert(
                    0, bottle_records[sv2.get()]["measurement unit"]
                )
                self.refill_bottle_cost_ent.insert(0, bottle_records[sv2.get()]["cost"])

        sv2 = ctk.StringVar()
        sv2.trace("w", lambda name, index, mode, sv2=sv2: trace_refill_serial_ent(sv2))
        self.refill_tab = ctk.CTkFrame(
            self.mainbar, border_color="#1FADFF", border_width=1
        )
        # ctk.CTkLabel(self.refill_tab, text=quick_variables.CustomCalendar.date_today()).pack(pady=(1, 0))

        self.fillorder_variable = ctk.StringVar()
        self.onorders_frame = ctk.CTkFrame(
            self.refill_tab,
            corner_radius=10,
        )
        self.onorders_frame.pack(fill="x", padx=10, pady=(10, 0))
        ctk.CTkLabel(self.onorders_frame, text="Fill an order?").pack(
            side="left", padx=5
        )
        self.pending_orders_menu = ctk.CTkOptionMenu(
            self.onorders_frame, variable=self.fillorder_variable
        )
        self.pending_orders_menu.set("--Fill an order--")
        self.pending_orders_menu.pack(padx=0, side="right")

        self.input_frame = ctk.CTkFrame(self.refill_tab, corner_radius=15)
        self.input_frame.pack(expand="yes", pady=10)
        ctk.CTkLabel(self.input_frame, text="Serial NO").grid(
            row=0, column=0, padx=5, pady=5
        )
        self.refill_bottle_serialno_ent = ctk.CTkComboBox(
            self.input_frame, variable=sv2
        )
        self.refill_bottle_serialno_ent.grid(row=0, column=1, padx=(0, 5), pady=5)
        self.refill_bottle_serialno_ent.set("")
        ctk.CTkLabel(self.input_frame, text="Bottle size").grid(
            row=1, column=0, padx=5, pady=(0, 5)
        )
        self.refill_bottle_size_ent = ctk.CTkEntry(self.input_frame)
        self.refill_bottle_size_ent.grid(row=1, column=1, padx=(0, 5), pady=(0, 5))
        ctk.CTkLabel(self.input_frame, text="Unit").grid(
            row=2, column=0, padx=5, pady=(0, 5)
        )
        self.refill_bottle_unit_ent = ctk.CTkEntry(self.input_frame)
        self.refill_bottle_unit_ent.grid(row=2, column=1, padx=(0, 5), pady=(0, 5))
        ctk.CTkLabel(self.input_frame, text="Cost").grid(
            row=3, column=0, padx=5, pady=(0, 5)
        )
        self.refill_bottle_cost_ent = ctk.CTkEntry(self.input_frame)
        self.refill_bottle_cost_ent.grid(row=3, column=1, padx=(0, 5), pady=(0, 5))
        self.refill_refill_button = ctk.CTkButton(
            self.refill_tab,
            height=40,
            fg_color="transparent",
            hover_color="#1FADFF",
            border_width=1,
            font=ctk.CTkFont("Rockwell Extra Bold", 16),
            text="Dispense",
            command=self.dispense,
        )
        self.refill_refill_button.pack(side="bottom", fill="x", padx=10, pady=10)
        self.profile_button = ctk.CTkButton(
            self.mainbar,
            corner_radius=0,
            anchor="w",
            border_spacing=10,
            height=40,
            hover_color=("gray70", "gray30"),
            fg_color="transparent",
            image=ctk.CTkImage(Image.open("./images/username_icon.png"), size=(30, 30)),
            compound="right",
        )
        self.profile_button.grid(row=0, column=0, sticky="ne")

        self.ordernumsTracker = ctk.StringVar()
        self.homebutton = ctk.CTkButton(
            self.leftsidebar,
            corner_radius=0,
            anchor="w",
            border_spacing=10,
            height=40,
            text_color=("gray10", "gray90"),
            hover_color="gray30",
            fg_color="transparent",
            text="HISTORY",
            image=ctk.CTkImage(Image.open("./images/home.png"), size=(30, 30)),
            compound="left",
            command=self.open_home,
        )
        self.homebutton.pack(fill="x")
        self.homebutton.bind(
            "<Double-Button-1>",
            lambda event: [
                self.destroy_open_dash_widgets(),
                self.highlight(self.homebutton),
            ],
        )

        self.transactionsbutton = ctk.CTkButton(
            self.leftsidebar,
            corner_radius=0,
            anchor="w",
            border_spacing=10,
            height=40,
            text_color=("gray10", "gray90"),
            hover_color="gray30",
            fg_color="transparent",
            textvariable=self.ordernumsTracker,
            image=ctk.CTkImage(Image.open("./images/receipt-ico.webp"), size=(30, 30)),
            compound="left",
            command=self.open_customers_tab,
        )
        self.transactionsbutton.pack(fill="x")

        self.receiptsbutton = ctk.CTkButton(
            self.leftsidebar,
            corner_radius=0,
            anchor="w",
            border_spacing=10,
            height=40,
            text_color=("gray10", "gray90"),
            hover_color="gray30",
            fg_color="transparent",
            text="Receipts",
            image=ctk.CTkImage(Image.open("./images/receipt1.png"), size=(35, 35)),
            compound="left",
            command=self.open_receipts_tab,
        )
        self.receiptsbutton.pack(fill="x")

        self.dispensorbutton = ctk.CTkButton(
            self.leftsidebar,
            corner_radius=0,
            anchor="w",
            border_spacing=10,
            height=40,
            text_color=("gray10", "gray90"),
            hover_color="gray30",
            fg_color="transparent",
            text="Dispensor",
            command=self.open_refill_tab,
            image=ctk.CTkImage(Image.open("./images/bottle_refill.jpg"), size=(50, 50)),
            compound="left",
        )
        self.dispensorbutton.pack(side="top", fill="x", pady=(80, 0))

        self.bottlesbutton = ctk.CTkButton(
            self.leftsidebar,
            corner_radius=0,
            anchor="w",
            border_spacing=10,
            height=40,
            text_color=("gray10", "gray90"),
            hover_color="gray30",
            fg_color="transparent",
            text="My Bottles",
            image=ctk.CTkImage(Image.open("./images/cost_tag.png"), size=(50, 70)),
            compound="left",
            command=self.open_bottles_tab,
        )
        self.bottlesbutton.pack(side="top", fill="x")

        self.logoutbutton = ctk.CTkButton(
            self.leftsidebar,
            anchor="w",
            border_spacing=10,
            corner_radius=0,
            height=40,
            text_color=("gray10", "gray90"),
            hover_color="gray30",
            fg_color="transparent",
            text="Log out",
            image=ctk.CTkImage(Image.open("./images/logout.png")),
            compound="left",
            command=self.logoutmerchant,
        )
        self.logoutbutton.pack(side="bottom", fill="x")

        ctk.CTkButton(
            self.login_form,
            command=lambda: self.login(
                self.user_name_entry.get(), self.password_entry.get()
            ),
            text="Log in",
        ).grid(row=3, column=1, padx=(0, 10), pady=(10, 0), sticky="e")

        ctk.CTkButton(
            self.login_form,
            command=self.create_account,
            height=40,
            text_color="black",
            fg_color="transparent",
            hover_color="#E9D5CD",
            corner_radius=0,
            text="Create an account",
        ).grid(row=4, column=0, columnspan=2, padx=5, pady=(190, 0), sticky="swe")

        self.bind(
            "<Return>",
            lambda dummyarg: self.login(
                self.user_name_entry.get(), self.password_entry.get()
            ),
        )
        self.prevclick = self.homebutton

    def highlight(self, clicked):
        clicked.configure(fg_color="grey50")
        clicked.configure(hover_color="grey50")
        self.prevclick.configure(fg_color="transparent")
        self.prevclick = clicked

    def destroy_open_dash_widgets(self):
        """Destroy all widgets in the dash"""
        for widget in self.open_dash_widgets:
            widget.grid_forget()

    def open_customers_tab(self):
        self.highlight(self.transactionsbutton)
        self.dynamic_text.set("Orders")
        self.destroy_open_dash_widgets()
        customers_table.grid(row=0, column=0)
        self.open_dash_widgets.append(customers_table)

    def open_bottles_tab(self):
        self.highlight(self.bottlesbutton)
        self.dynamic_text.set("Bottles")
        self.destroy_open_dash_widgets()
        self.bottles_tab.grid(row=0, column=0, sticky="nwse", padx=180, pady=180)
        self.open_dash_widgets.append(self.bottles_tab)

    def open_home(self):
        self.highlight(self.homebutton)
        self.dynamic_text.set("Home")
        self.destroy_open_dash_widgets()
        sales_table.grid(
            row=0,
            column=0,
        )
        self.open_dash_widgets.append(sales_table)

    def open_refill_tab(self):
        self.highlight(self.dispensorbutton)
        self.dynamic_text.set("Dispense")
        self.destroy_open_dash_widgets()
        self.refill_tab.grid(row=0, column=0, sticky="nwse", padx=180, pady=170)
        self.open_dash_widgets.append(self.refill_tab)

    def open_receipts_tab(self):
        self.highlight(self.receiptsbutton)
        self.dynamic_text.set("Download receipts")
        self.destroy_open_dash_widgets()
        self.downloadall.grid(row=0, column=0, padx=(150, 0), sticky="w")
        self.download_button.grid(row=0, column=0, padx=(0, 150), sticky="e")
        self.open_dash_widgets.extend([self.downloadall, self.download_button])

    def fetch_order(self, orderid):
        """Fetch an order"""
        try:
            result = next(
                (
                    i[3]
                    for i in database.fetch_orders(self.loggedin_username.get())
                    if i[0] == int(orderid)
                ),
                "None",
            )
            self.refill_bottle_serialno_ent.set(result)
        except ValueError:
            self.refill_bottle_serialno_ent.set("")

    def customer_view_orders(self, customer_usernamme):
        """Shows orders placed on the customer's side"""
        window = ctk.CTkToplevel()
        window.overrideredirect(True)
        window.wm_attributes("-topmost", True)

        columns = [
            {"text": "Number", "stretch": False},
            {"text": "Customer", "stretch": False},
            {"text": "Merchant", "stretch": False},
            {"text": "Bottle NO", "stretch": False},
            {"text": "Description", "stretch": False},
            {"text": "Price", "stretch": False},
            {"text": "Date of order", "stretch": False},
            {"text": "Time of order", "stretch": False},
            {"text": "status", "stretch": False},
            {"text": "delivery date", "stretch": False},
            {"text": "time of delivery", "stretch": False},
        ]

        if database.fetch_customer_notifications(self.loggedin_username.get()) > 0:
            _rowdata = database.fetch_cached_orders(self.loggedin_username.get())
            database.cnx.commit()
            database.delete_cached_orders(self.loggedin_username.get())
            self.customerNotificationTracker.set("History")
            button_text = "Close notifications"
        else:
            button_text = "CLOSE"
            _rowdata = database.cfetch_orders(self.loggedin_username.get())

        from ttkbootstrap import tableview

        table = tableview.Tableview(
            window,
            height=30,
            stripecolor=("light green", None),
            coldata=columns,
            rowdata=_rowdata,
            paginated=False,
            autofit=True,
            searchable=True,
            bootstyle="success",
        )
        table.pack(padx=20, pady=20, expand="yes")

        start_x = 0
        start_y = 0

        def start_drag(event):
            nonlocal start_x, start_y
            start_x = event.x
            start_y = event.y

        def drag(event):
            delta_x = event.x - start_x
            delta_y = event.y - start_y
            x = window.winfo_x() + delta_x
            y = window.winfo_y() + delta_y
            window.geometry(f"+{x}+{y}")

        window.bind("<ButtonPress-1>", start_drag)
        window.bind("<B1-Motion>", drag)
        ctk.CTkButton(
            window,
            text=button_text,
            height=40,
            font=ctk.CTkFont("Arial", 16, "bold", "roman"),
            command=window.destroy,
        ).pack(pady=20, expand="yes")
        window.mainloop()

    def dispense(self):
        response = database.dispense(
            self.loggedin_username.get(),
            self.refill_bottle_serialno_ent.get(),
            self.refill_bottle_cost_ent.get(),
        )
        if "Would you like to proceed?" in response:
            if askyesnocancel("TheosWaters", response):
                receipt_path = f'./receipts/{quick_variables.CustomCalendar.date_today()}@{quick_variables.CustomCalendar.time_now().replace(":", "-")}-{"".join([random.choice(string.digits) for i in range(8+1)])}.pdf'
                if self.fillorder_variable.get().isdigit():
                    if askyesno(
                        "TheosWaters",
                        "We have detected that you are filling an order. Continue filling as an order?",
                    ):
                        database.fill_order(self.fillorder_variable.get())
                        database.cnx.commit()
                        self.pending_orders_menu.configure(
                            values=["-"]
                            + [
                                str(i[0])
                                for i in database.fetch_orders(
                                    self.loggedin_username.get()
                                )
                                if i[8] == "pending"
                            ]
                        )
                        global customers_table
                        from ttkbootstrap.tableview import Tableview

                        customers_table = Tableview(
                            master=self.mainbar,
                            height=30,
                            bootstyle="success",
                            stripecolor=("light green", None),
                            coldata=customer_columns,
                            rowdata=database.fetch_orders(self.loggedin_username.get()),
                            paginated=False,
                            autofit=True,
                            searchable=True,
                        )
                        self.ordernumsTracker.set(
                            f'Orders ({len([i for i in database.fetch_orders(self.loggedin_username.get()) if i[8] == "pending"])})'
                        )
                        cname = [
                            i[1]
                            for i in database.fetch_orders(self.loggedin_username.get())
                            if str(i[0]) == self.fillorder_variable.get()
                        ][0]
                        customer_notifications: int = (
                            database.fetch_customer_notifications(cname)
                        )
                        customer_notifications += 1
                        database.update_value(
                            "customers",
                            "notifications",
                            customer_notifications,
                            "username",
                            cname,
                        )
                        database.cache_order(self.fillorder_variable.get())
                        self.fillorder_variable.set(
                            f"Order {self.fillorder_variable.get()} ({cname}) filled"
                        )

                        reports.generate_receipt(
                            receipt_path,
                            cname,
                            quick_variables.CustomCalendar.date_today(),
                            quick_variables.CustomCalendar.time_now(),
                            f"{self.refill_bottle_size_ent.get()} {self.refill_bottle_unit_ent.get()}",
                            self.refill_bottle_cost_ent.get(),
                            self.loggedin_username.get(),
                        )
                    else:
                        self.pending_orders_menu.set("-")
                        reports.generate_receipt(
                            receipt_path,
                            "-",
                            quick_variables.CustomCalendar.date_today(),
                            quick_variables.CustomCalendar.time_now(),
                            f"{self.refill_bottle_size_ent.get()} {self.refill_bottle_unit_ent.get()}",
                            self.refill_bottle_cost_ent.get(),
                            self.loggedin_username.get(),
                        )
                else:
                    reports.generate_receipt(
                        receipt_path,
                        "-",
                        quick_variables.CustomCalendar.date_today(),
                        quick_variables.CustomCalendar.time_now(),
                        f"{self.refill_bottle_size_ent.get()} {self.refill_bottle_unit_ent.get()}",
                        self.refill_bottle_cost_ent.get(),
                        self.loggedin_username.get(),
                    )
                self.latestreceiptvar.set(receipt_path)

                global sales_table
                sales_columns = [
                    {"text": "Number", "stretch": False},
                    {"text": "Bottle description", "stretch": False},
                    {"text": "Cost", "stretch": False},
                    {"text": "Date", "stretch": False},
                    {"text": "Day", "stretch": False},
                    {"text": "Time", "stretch": False},
                ]
                from ttkbootstrap.tableview import Tableview

                sales_table = Tableview(
                    master=self.mainbar,
                    height=30,
                    stripecolor=("light blue", None),
                    coldata=sales_columns,
                    rowdata=database.fetch_sales(self.loggedin_username.get()),
                    paginated=False,
                    autofit=True,
                    searchable=True,
                    bootstyle="success",
                )
                database.cnx.commit()
                self.refill_refill_button.configure(state="disabled")
                dispense_window = ctk.CTkToplevel()
                dispense_window.overrideredirect(True)
                dispense_window.geometry("450x150")
                dispense_window.title("TheosWaters")
                dispense_window.resizable(False, False)
                dispense_window.wm_attributes("-topmost", True)
                progress_message = ctk.CTkLabel(
                    dispense_window,
                    font=ctk.CTkFont("Arial", 30, "bold", "roman"),
                    text="Dispensing...",
                )
                progress_message.pack(pady=(40, 20))
                progressbar = ttk.Progressbar(
                    dispense_window, maximum=100, mode="determinate", length=300
                )
                progressbar.pack(fill="x", padx=20, pady=(0, 40))
                progressbar.start(100)
                self.after(
                    10500,
                    lambda: [
                        dispense_window.destroy(),
                        self.refill_refill_button.configure(state="normal"),
                        showinfo("TheosWaters", "Completed successfully"),
                    ],
                )
        else:
            showerror("TheosWaters", response)

    def download_receipts(self, how_many):
        if not os.path.exists("./archived receipts"):
            os.mkdir("./archived receipts")

        if how_many == "one":
            if self.latestreceiptvar.get():
                path = askdirectory(initialdir=reports.default_receipts_path)
                file = self.latestreceiptvar.get()
                shutil.copy(file, path + "/" + os.path.basename(file))
                shutil.move(file, f"./archived receipts/{os.path.basename(file)}")
                os.startfile(path + "/" + os.path.basename(file))
                self.latestreceiptvar.set("")
            else:
                showinfo(
                    "",
                    "We seem to not any current receipts. Please start serving orders to download receipts.",
                )
        else:
            if glob.glob("./receipts/*.pdf"):
                path = askdirectory(initialdir=reports.default_receipts_path)
                if askyesnocancel(
                    len(glob.glob("./receipts/*.pdf")),
                    f"{len(glob.glob('./receipts/*.pdf'))} receipts will be downloaded. Do you want to proceed?",
                ):
                    for file in glob.glob("./receipts/*.pdf"):
                        shutil.copy(file, path + "/" + os.path.basename(file))
                        shutil.move(
                            file, f"./archived receipts/{os.path.basename(file)}"
                        )
                    showinfo(
                        "",
                        f"The receipts have been downloaded successfully. Find theme here: {path}",
                    )
            else:
                showinfo(
                    "",
                    "We seem to not find any receipts. Please start serving orders to download receipts.",
                )

    def create_account(self):
        """Create a user account"""
        window = ctk.CTkToplevel()
        window.overrideredirect(True)
        window.wm_attributes("-topmost", True)
        window.geometry("450x550")
        start_x = 0
        start_y = 0

        def start_drag(event):
            nonlocal start_x, start_y
            start_x = event.x
            start_y = event.y

        def drag(event):
            delta_x = event.x - start_x
            delta_y = event.y - start_y
            x = window.winfo_x() + delta_x
            y = window.winfo_y() + delta_y
            window.geometry(f"+{x}+{y}")

        def password_strong(password) -> bool:
            pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$"
            return re.match(pattern, password) is not None

        def authenticate(usertype, username, password1, password2) -> str:
            if not username or not password1 or not password2:
                return "Leaving any of the fields blank is not allowed!"

            if usertype not in ["merchant", "customer"]:
                return "You have not selected a user type"

            if password1 != password2:
                return "The passwords you entered don't match!"

            if not password_strong(password1):
                return "The password is not strong enough!"

            if (
                username
                in database.fetch_customers() + database.fetch_merchant_usernames()
            ):
                return (
                    "The username `%s` cannot be used! Please try another one"
                    % username
                )

            return (
                "Everything looks set! You can now log in using the given credentials"
            )

        def finish_signup():
            response = authenticate(
                user_type_entry.get(),
                username_entry.get(),
                password1_entry.get(),
                password2_entry.get(),
            )
            if "Everything looks set!" in response:
                if askyesnocancel(
                    "SUGNUP-theoswaters",
                    "This will add you in the database. Do you wnt to proceed?",
                    parent=window,
                ):
                    database.add_user(
                        user_type_entry.get(),
                        username_entry.get(),
                        password1_entry.get(),
                    )
            showinfo("", response, parent=window)

        title_bar = ctk.CTkFrame(window)
        title_bar.pack(padx=10, pady=10, fill="x")

        title_bar.bind("<ButtonPress-1>", start_drag)
        title_bar.bind("<B1-Motion>", drag)

        ctk.CTkLabel(
            title_bar,
            text_color="#FEF9C3",
            text="SIGNUP",
            font=ctk.CTkFont("Arial", 18, "bold"),
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            title_bar,
            command=window.destroy,
            corner_radius=0,
            text_color="black",
            fg_color="#E9D5CD",
            hover_color="#FEF9C3",
            width=60,
            text="Close",
        ).pack(side="right")

        form = ctk.CTkFrame(window, corner_radius=20)
        username_label = ctk.CTkLabel(form, text="Username")
        username_label.grid(row=0, column=0, padx=5, pady=(10, 5))

        password1_label = ctk.CTkLabel(form, text="Password")
        password1_label.grid(row=1, column=0, padx=5, pady=(0, 5))

        password2_label = ctk.CTkLabel(form, text="Retype password")
        password2_label.grid(row=2, column=0, padx=5, pady=(0, 10))

        username_entry = ctk.CTkEntry(form, width=200)
        username_entry.grid(row=0, column=1, padx=5, pady=(10, 5))

        password1_entry = ctk.CTkEntry(form, width=200, show="•")
        password1_entry.grid(row=1, column=1, padx=5, pady=(0, 5))

        password2_entry = ctk.CTkEntry(form, width=200, show="•")
        password2_entry.grid(row=2, column=1, padx=5, pady=(0, 5))

        user_type_entry = ctk.CTkOptionMenu(
            form,
            values=["merchant", "customer"],
            width=200,
            text_color="white",
            fg_color="#343638",
        )
        user_type_entry.set("Select user type...")
        user_type_entry.grid(row=3, column=1, padx=5, pady=(0, 10))

        form.pack(pady=(100, 50))

        ctk.CTkButton(
            window,
            command=finish_signup,
            height=40,
            text_color="black",
            fg_color="#E9D5CD",
            width=300,
            hover_color="#FEF9C3",
            corner_radius=10,
            text="Create an account",
        ).pack()

    def login(self, username, password):
        """Authenticates username and password, if successful the dashboard is displayed"""
        database_login_response = database.login_success(username, password)
        if database_login_response["is_successful"]:
            self.login_form.grid_forget()
            self.loggedin_username.set(username)
            if database_login_response["user_type"] == "merchant":
                """Call the merchants dashboard"""
                self.ordernumsTracker.set(
                    f'Orders ({len([i for i in database.fetch_orders(self.loggedin_username.get()) if i[8] == "pending"])})'
                )
                self.merchant_dashboard.grid(row=0, column=0, sticky="nwse")
                self.profile_button.configure(text=self.loggedin_username.get())
                global customer_columns
                customer_columns = [
                    {"text": "Number", "stretch": False},
                    {"text": "Customer", "stretch": False},
                    {"text": "Merchant", "stretch": False},
                    {"text": "Bottle NO", "stretch": False},
                    {"text": "Description", "stretch": False},
                    {"text": "Price", "stretch": False},
                    {"text": "Date of order", "stretch": False},
                    {"text": "Time of order", "stretch": False},
                    {"text": "status", "stretch": False},
                    {"text": "delivery date", "stretch": False},
                    {"text": "time of delivery", "stretch": False},
                ]

                sales_columns = [
                    {"text": "Number", "stretch": False},
                    {"text": "Bottle description", "stretch": False},
                    {"text": "Cost", "stretch": False},
                    {"text": "Date", "stretch": False},
                    {"text": "Day", "stretch": False},
                    {"text": "Time", "stretch": False},
                ]
                from ttkbootstrap.tableview import Tableview

                global bottle_records
                global bottle_serial_numbers
                global customers_table
                global sales_table

                customers_table = Tableview(
                    master=self.mainbar,
                    height=30,
                    bootstyle="success",
                    stripecolor=("light green", None),
                    coldata=customer_columns,
                    rowdata=database.fetch_orders(self.loggedin_username.get()),
                    paginated=False,
                    autofit=True,
                    searchable=True,
                )
                sales_table = Tableview(
                    master=self.mainbar,
                    height=30,
                    bootstyle="success",
                    stripecolor=("light blue", None),
                    coldata=sales_columns,
                    rowdata=database.fetch_sales(username),
                    paginated=False,
                    autofit=True,
                    searchable=True,
                )

                self.bottles: list[tuple] = database.fetch_bottles(username)
                bottle_records = {}
                for record in self.bottles:
                    bottle_records[str(record[0])] = {
                        "bottle size": record[1],
                        "measurement unit": record[2],
                        "cost": record[3],
                    }
                bottle_serial_numbers = list(bottle_records.keys())
                self.bottle_serialno_ent.configure(values=bottle_serial_numbers)
                self.refill_bottle_serialno_ent.configure(values=bottle_serial_numbers)
                self.pending_orders_menu.configure(
                    values=["-"]
                    + [
                        str(i[0])
                        for i in database.fetch_orders(self.loggedin_username.get())
                        if i[8] == "pending"
                    ]
                )
                self.pending_orders_menu.configure(
                    command=lambda value: self.fetch_order(
                        self.pending_orders_menu.get()
                    )
                )
            else:
                """Call the customers dashboard"""
                self.balancetag_variable.set(
                    f"Your balance is KES{database.fetch_customer_balance(self.loggedin_username.get())}"
                )
                self.customerdashboard.grid(row=0, column=0)
                self.welcome_message.configure(
                    text="Hi "
                    + self.loggedin_username.get().capitalize()
                    + "! Use the dropdown to search or select a merchant."
                )
                notifications = database.fetch_customer_notifications(
                    self.loggedin_username.get()
                )
                if notifications > 0:
                    self.orderstag.configure(
                        fg_color="dark green", hover_color="green", text_color="white"
                    )
                self.customerNotificationTracker.set(
                    f"You have {notifications} new notifications"
                )
        else:
            showwarning("Water Management System", "FAIL! Invalid username or password")

    def logoutcustomer(self):
        """Logs out the customer"""
        if askyesnocancel("TheosWaters", "Are you sure you want to log out?"):
            self.customerdashboard.grid_forget()
            self.login_form.grid(row=0, column=0, sticky="ns", pady=50)
            self.merchant_username_ent.set("--SELECT--")
            try:
                for i in (
                    refill_bottle_size_ent,
                    refill_bottle_unit_ent,
                    refill_bottle_cost_ent,
                ):
                    i.delete(0, "end")
            except NameError:
                pass

    def logoutmerchant(self):
        """Logs out the user"""
        self.highlight(self.logoutbutton)
        if askyesnocancel(
            "Water management system",
            "This will log you out. Are you sure you want to log out?",
        ):
            customers_table.grid_forget()
            self.bottle_serialno_ent.set("")
            self.refill_bottle_serialno_ent.set("")
            for field in [
                self.bottle_size_ent,
                self.bottle_unit_ent,
                self.bottle_cost_ent,
                self.refill_bottle_size_ent,
                self.refill_bottle_unit_ent,
                self.refill_bottle_cost_ent,
            ]:
                field.delete(0, "end")
            self.merchant_dashboard.grid_forget()
            self.login_form.grid(row=0, column=0, sticky="ns", pady=50)
            self.destroy_open_dash_widgets()


ctk.set_appearance_mode(
    "Dark"
)  # ?: I have optimized the UI for dark mode. Change to Light and see things get wonky
ctk.set_default_color_theme("dark-blue")

if not os.path.exists('receipts'):
    os.mkdir('receipts')

if __name__ == "__main__":
    app = App()
    app.mainloop()
# App ends here...
