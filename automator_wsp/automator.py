import flet as ft
import pywhatkit as kit
import json
import os
import webbrowser
import logging
import multiprocessing
from datetime import datetime, date
from plyer import notification

logging.basicConfig(
    filename="automator.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class PERSONAutomator:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "PERSON Automator"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 0
        self.page.window.width = 420
        self.page.window.height = 900
        self.page.window.resizable = True
        self.page.window.min_width = 350
        self.page.window.min_height = 600
        self.page.bgcolor = ft.colors.GREY_900

        self.settings_file = "PERSON_settings.json"
        self.history_file = "send_history.json"
        self.schedule_file = "schedule.json"
        self.settings = self.load_settings()
        self.history = self.load_history()
        self.scheduler_process = None

        self.setup_ui()

    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, "r") as f:
                    return json.load(f)
        except Exception as e:
            logging.error(f"Error loading settings: {str(e)}")
            self.show_alert(f"Error loading settings: {str(e)}", ft.colors.RED_400)
        return {
            "number": "",
            "message": "Despierta, bro!",
            "day": str(date.today().day),
            "month": str(date.today().month),
            "year": str(date.today().year),
            "hour": "5",
            "minute": "0"
        }

    def save_settings(self):
        try:
            settings = {
                "number": self.number_field.value,
                "message": self.message_field.value,
                "day": self.day_field.value,
                "month": self.month_field.value,
                "year": self.year_field.value,
                "hour": self.hour_field.value,
                "minute": self.minute_field.value
            }
            with open(self.settings_file, "w") as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving settings: {str(e)}")
            self.show_alert(f"Error saving settings: {str(e)}", ft.colors.RED_400)

    def load_history(self):
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, "r") as f:
                    return json.load(f)
        except Exception as e:
            logging.error(f"Error loading history: {str(e)}")
            self.show_alert(f"Error loading history: {str(e)}", ft.colors.RED_400)
        return []

    def save_history(self, number, message, status, error=None):
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            history_entry = {
                "timestamp": timestamp,
                "number": number,
                "message": message,
                "status": status,
                "error": error if error else ""
            }
            self.history.append(history_entry)
            with open(self.history_file, "w") as f:
                json.dump(self.history, f, indent=2)
            self.update_history_view()
        except Exception as e:
            logging.error(f"Error saving history: {str(e)}")
            self.show_alert(f"Error saving history: {str(e)}", ft.colors.RED_400)

    def validate_inputs(self):
        number = self.number_field.value
        message = self.message_field.value
        try:
            day = int(self.day_field.value)
            month = int(self.month_field.value)
            year = int(self.year_field.value)
            hour = int(self.hour_field.value)
            minute = int(self.minute_field.value)
            if not (1 <= day <= 31):
                return None, "Day must be between 1 and 31."
            if not (1 <= month <= 12):
                return None, "Month must be between 1 and 12."
            if not (2025 <= year <= 2030):
                return None, "Year must be between 2025 and 2030."
            if not (0 <= hour <= 23):
                return None, "Hour must be between 0 and 23."
            if not (0 <= minute <= 59):
                return None, "Minute must be between 0 and 59."
            if not number.startswith("+569") or len(number) != 12:
                return None, "Invalid Chilean phone number. Use +569 followed by 8 digits."
            if not message.strip():
                return None, "Message cannot be empty."
            try:
                datetime(year, month, day, hour, minute)
                if datetime(year, month, day, hour, minute) < datetime.now():
                    return None, "Scheduled date and time must be in the future."
            except ValueError:
                return None, "Invalid date."
            return (day, month, year, hour, minute, number, message), None
        except ValueError:
            return None, "Date, hour, and minute must be valid numbers."

    def send_PERSON(self, number, message, hour, minute):
        try:
            logging.info(f"Attempting to send message to {number} at {hour:02d}:{minute:02d}")
            kit.sendwhatmsg(number, message, hour, minute, wait_time=40, tab_close=True)
            self.save_history(number, message, "Success")
            self.show_alert("Message sent successfully!", ft.colors.GREEN_400)
            self.show_notification("PERSON Automator", "Message sent successfully!")
            logging.info(f"Message sent successfully to {number}")
        except Exception as e:
            self.save_history(number, message, "Failed", str(e))
            self.show_alert(f"Failed to send message: {str(e)}", ft.colors.RED_400)
            self.show_notification("PERSON Automator", f"Failed to send message: {str(e)}")
            logging.error(f"Failed to send message to {number}: {str(e)}")

    def test_send(self, e):
        inputs, error = self.validate_inputs()
        if error:
            self.show_alert(error, ft.colors.RED_400)
            self.show_notification("PERSON Automator", error)
            logging.error(f"Test send failed: {error}")
            return
        _, _, _, _, _, number, message = inputs
        try:
            logging.info(f"Test sending message to {number}")
            kit.sendwhatmsg_instantly(number, message, wait_time=40, tab_close=True)
            self.save_history(number, message, "Success")
            self.show_alert("Test message sent successfully!", ft.colors.GREEN_400)
            self.show_notification("PERSON Automator", "Test message sent successfully!")
            logging.info(f"Test message sent successfully to {number}")
        except Exception as e:
            self.save_history(number, message, "Failed", str(e))
            self.show_alert(f"Failed to send test message: {str(e)}", ft.colors.RED_400)
            self.show_notification("PERSON Automator", f"Failed to send test message: {str(e)}")
            logging.error(f"Test send failed to {number}: {str(e)}")

    def show_alert(self, message, color):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Row([
                ft.Icon(ft.icons.INFO_OUTLINE, color=ft.colors.WHITE),
                ft.Text(message, color=ft.colors.WHITE, weight=ft.FontWeight.W_500)
            ], spacing=10),
            bgcolor=color,
            duration=4000,
            elevation=10
        )
        self.page.snack_bar.open = True
        self.page.update()

    def show_notification(self, title, message):
        try:
            notification.notify(title=title, message=message, app_name="PERSON Automator", timeout=5)
        except Exception as e:
            self.show_alert(f"Notification error: {str(e)}", ft.colors.RED_400)
            logging.error(f"Notification error: {str(e)}")

    def schedule_message(self, e):
        inputs, error = self.validate_inputs()
        if error:
            self.show_alert(error, ft.colors.RED_400)
            self.show_notification("PERSON Automator", error)
            logging.error(f"Schedule failed: {error}")
            return
        day, month, year, hour, minute, number, message = inputs
        try:
            schedule_data = {
                "number": number,
                "message": message,
                "day": day,
                "month": month,
                "year": year,
                "hour": hour,
                "minute": minute,
                "active": True
            }
            with open(self.schedule_file, "w") as f:
                json.dump(schedule_data, f, indent=2)
            self.save_settings()
            self.show_alert(f"Message scheduled for {year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}.", ft.colors.BLUE_400)
            self.show_notification("PERSON Automator", f"Message scheduled for {year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}.")
            logging.info(f"Message scheduled for {number} at {year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}")
            if not hasattr(self, "scheduler_process") or not self.scheduler_process.is_alive():
                self.scheduler_process = multiprocessing.Process(target=run_scheduler, args=(self.schedule_file,))
                self.scheduler_process.daemon = True
                self.scheduler_process.start()
                logging.info("Background scheduler process started")
        except Exception as e:
            self.show_alert(f"Error scheduling message: {str(e)}", ft.colors.RED_400)
            logging.error(f"Error scheduling message: {str(e)}")

    def open_PERSON_web(self, e):
        try:
            webbrowser.open("https://web.PERSON.com")
            self.show_alert("PERSON Web opened. Please scan the QR code to log in.", ft.colors.BLUE_400)
            self.show_notification("PERSON Automator", "PERSON Web opened. Please scan the QR code to log in.")
            logging.info("Opened PERSON Web for login")
        except Exception as e:
            self.show_alert(f"Error opening PERSON Web: {str(e)}", ft.colors.RED_400)
            logging.error(f"Error opening PERSON Web: {str(e)}")

    def show_date_picker(self, e):
        def on_confirm(e):
            self.day_field.value = day_dropdown.value
            self.month_field.value = month_dropdown.value
            self.year_field.value = year_dropdown.value
            self.page.dialog.open = False
            self.page.update()

        def on_cancel(e):
            self.page.dialog.open = False
            self.page.update()

        day_dropdown = ft.Dropdown(
            label="Day",
            value=self.day_field.value,
            options=[ft.dropdown.Option(str(i)) for i in range(1, 32)],
            width=100,
            bgcolor=ft.colors.GREY_800,
            color=ft.colors.WHITE,
            border_color=ft.colors.BLUE_400
        )
        month_dropdown = ft.Dropdown(
            label="Month",
            value=self.month_field.value,
            options=[ft.dropdown.Option(str(i)) for i in range(1, 13)],
            width=100,
            bgcolor=ft.colors.GREY_800,
            color=ft.colors.WHITE,
            border_color=ft.colors.BLUE_400
        )
        year_dropdown = ft.Dropdown(
            label="Year",
            value=self.year_field.value,
            options=[ft.dropdown.Option(str(i)) for i in range(2025, 2031)],
            width=100,
            bgcolor=ft.colors.GREY_800,
            color=ft.colors.WHITE,
            border_color=ft.colors.BLUE_400
        )
        dialog = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.icons.CALENDAR_TODAY, color=ft.colors.BLUE_400),
                ft.Text("Select Date", color=ft.colors.WHITE, weight=ft.FontWeight.BOLD)
            ], spacing=10),
            content=ft.Row([day_dropdown, month_dropdown, year_dropdown], spacing=10, alignment=ft.MainAxisAlignment.CENTER),
            actions=[
                ft.TextButton("OK", on_click=on_confirm, style=ft.ButtonStyle(color=ft.colors.BLUE_400)),
                ft.TextButton("Cancel", on_click=on_cancel, style=ft.ButtonStyle(color=ft.colors.GREY_400))
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=ft.colors.GREY_900
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def show_time_picker(self, e):
        def on_confirm(e):
            self.hour_field.value = hour_dropdown.value
            self.minute_field.value = minute_dropdown.value
            self.page.dialog.open = False
            self.page.update()

        def on_cancel(e):
            self.page.dialog.open = False
            self.page.update()

        hour_dropdown = ft.Dropdown(
            label="Hour",
            value=self.hour_field.value,
            options=[ft.dropdown.Option(str(i)) for i in range(24)],
            width=120,
            bgcolor=ft.colors.GREY_800,
            color=ft.colors.WHITE,
            border_color=ft.colors.GREEN_400
        )
        minute_dropdown = ft.Dropdown(
            label="Minute",
            value=self.minute_field.value,
            options=[ft.dropdown.Option(f"{i:02d}") for i in range(60)],
            width=120,
            bgcolor=ft.colors.GREY_800,
            color=ft.colors.WHITE,
            border_color=ft.colors.GREEN_400
        )
        dialog = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.icons.ACCESS_TIME, color=ft.colors.GREEN_400),
                ft.Text("Select Time", color=ft.colors.WHITE, weight=ft.FontWeight.BOLD)
            ], spacing=10),
            content=ft.Row([hour_dropdown, minute_dropdown], spacing=20, alignment=ft.MainAxisAlignment.CENTER),
            actions=[
                ft.TextButton("OK", on_click=on_confirm, style=ft.ButtonStyle(color=ft.colors.GREEN_400)),
                ft.TextButton("Cancel", on_click=on_cancel, style=ft.ButtonStyle(color=ft.colors.GREY_400))
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=ft.colors.GREY_900
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def update_history_view(self):
        self.history_container.content.controls.clear()
        for entry in self.history[-5:]:
            status_color = ft.colors.GREEN_400 if entry["status"] == "Success" else ft.colors.RED_400
            status_icon = ft.icons.CHECK_CIRCLE if entry["status"] == "Success" else ft.icons.ERROR
            
            self.history_container.content.controls.append(
                ft.Container(
                    content=ft.ListTile(
                        leading=ft.Icon(status_icon, color=status_color, size=24),
                        title=ft.Text(f"{entry['timestamp']}", color=ft.colors.WHITE, size=12, weight=ft.FontWeight.W_500),
                        subtitle=ft.Text(f"To: {entry['number']}\nMessage: {entry['message'][:30]}...", color=ft.colors.GREY_400, size=10),
                        trailing=ft.Icon(ft.icons.PERSON, color=ft.colors.GREEN if entry["status"] == "Success" else ft.colors.RED_400),
                    ),
                    bgcolor=ft.colors.GREY_800,
                    border_radius=10,
                    margin=ft.margin.only(bottom=5),
                    padding=5
                )
            )
        self.page.update()

    def toggle_history_view(self, e):
        self.history_container.visible = not self.history_container.visible
        if self.history_container.visible:
            e.control.text = "Hide History"
            e.control.icon = ft.icons.VISIBILITY_OFF
        else:
            e.control.text = "Show History"
            e.control.icon = ft.icons.HISTORY
        self.page.update()

    def save_and_exit(self, e):
        self.save_settings()
        inputs, error = self.validate_inputs()
        if not error:
            day, month, year, hour, minute, number, message = inputs
            try:
                schedule_data = {
                    "number": number,
                    "message": message,
                    "day": day,
                    "month": month,
                    "year": year,
                    "hour": hour,
                    "minute": minute,
                    "active": True
                }
                with open(self.schedule_file, "w") as f:
                    json.dump(schedule_data, f, indent=2)
                logging.info("Schedule saved on exit")
                if not hasattr(self, "scheduler_process") or not self.scheduler_process.is_alive():
                    self.scheduler_process = multiprocessing.Process(target=run_scheduler, args=(self.schedule_file,))
                    self.scheduler_process.daemon = True
                    self.scheduler_process.start()
                    logging.info("Background scheduler process started on exit")
            except Exception as e:
                self.show_alert(f"Error saving schedule on exit: {str(e)}", ft.colors.RED_400)
                logging.error(f"Error saving schedule on exit: {str(e)}")
        self.page.window.close()
        logging.info("Application closed")

    def get_responsive_width(self, base_width):
        window_width = self.page.window.width if self.page.window.width else 420
        return min(base_width, window_width * 0.9)

    def setup_ui(self):
        header = ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.PERSON, color=ft.colors.GREEN, size=32),
                ft.Text("PERSON Automator", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            bgcolor=ft.colors.GREY_800,
            padding=20,
            border_radius=ft.border_radius.only(bottom_left=15, bottom_right=15),
            margin=ft.margin.only(bottom=20)
        )

        self.number_field = ft.TextField(
            label="Phone Number",
            hint_text="+56912345678",
            value=self.settings.get("number", ""),
            prefix_icon=ft.icons.PHONE_ANDROID,
            bgcolor=ft.colors.GREY_800,
            color=ft.colors.WHITE,
            border_color=ft.colors.GREY_600,
            focused_border_color=ft.colors.GREEN_400,
            border_radius=12,
            text_size=14,
            label_style=ft.TextStyle(color=ft.colors.GREY_400)
        )

        self.message_field = ft.TextField(
            label="Message",
            value=self.settings.get("message", "Despierta, bro!"),
            prefix_icon=ft.icons.MESSAGE,
            bgcolor=ft.colors.GREY_800,
            color=ft.colors.WHITE,
            border_color=ft.colors.GREY_600,
            focused_border_color=ft.colors.BLUE_400,
            border_radius=12,
            text_size=14,
            multiline=True,
            min_lines=2,
            max_lines=4,
            label_style=ft.TextStyle(color=ft.colors.GREY_400)
        )

        date_section = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.icons.CALENDAR_TODAY, color=ft.colors.BLUE_400, size=20),
                    ft.Text("Schedule Date", color=ft.colors.WHITE, weight=ft.FontWeight.W_500)
                ], spacing=8),
                ft.Row([
                    ft.Container(
                        content=ft.TextField(
                            label="Day",
                            value=self.settings.get("day", str(date.today().day)),
                            bgcolor=ft.colors.GREY_800,
                            color=ft.colors.WHITE,
                            border_color=ft.colors.GREY_600,
                            focused_border_color=ft.colors.BLUE_400,
                            border_radius=8,
                            text_size=12,
                            text_align=ft.TextAlign.CENTER,
                            on_focus=self.show_date_picker,
                            label_style=ft.TextStyle(color=ft.colors.GREY_400, size=10)
                        ),
                        expand=1
                    ),
                    ft.Container(
                        content=ft.TextField(
                            label="Month",
                            value=self.settings.get("month", str(date.today().month)),
                            bgcolor=ft.colors.GREY_800,
                            color=ft.colors.WHITE,
                            border_color=ft.colors.GREY_600,
                            focused_border_color=ft.colors.BLUE_400,
                            border_radius=8,
                            text_size=12,
                            text_align=ft.TextAlign.CENTER,
                            on_focus=self.show_date_picker,
                            label_style=ft.TextStyle(color=ft.colors.GREY_400, size=10)
                        ),
                        expand=1
                    ),
                    ft.Container(
                        content=ft.TextField(
                            label="Year",
                            value=self.settings.get("year", str(date.today().year)),
                            bgcolor=ft.colors.GREY_800,
                            color=ft.colors.WHITE,
                            border_color=ft.colors.GREY_600,
                            focused_border_color=ft.colors.BLUE_400,
                            border_radius=8,
                            text_size=12,
                            text_align=ft.TextAlign.CENTER,
                            on_focus=self.show_date_picker,
                            label_style=ft.TextStyle(color=ft.colors.GREY_400, size=10)
                        ),
                        expand=1
                    )
                ], spacing=10)
            ], spacing=10),
            bgcolor=ft.colors.GREY_800,
            padding=15,
            border_radius=12,
            border=ft.border.all(1, ft.colors.GREY_700)
        )

        time_section = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.icons.ACCESS_TIME, color=ft.colors.GREEN_400, size=20),
                    ft.Text("Schedule Time", color=ft.colors.WHITE, weight=ft.FontWeight.W_500)
                ], spacing=8),
                ft.Row([
                    ft.Container(
                        content=ft.TextField(
                            label="Hour",
                            value=self.settings.get("hour", "5"),
                            bgcolor=ft.colors.GREY_800,
                            color=ft.colors.WHITE,
                            border_color=ft.colors.GREY_600,
                            focused_border_color=ft.colors.GREEN_400,
                            border_radius=8,
                            text_size=12,
                            text_align=ft.TextAlign.CENTER,
                            on_focus=self.show_time_picker,
                            label_style=ft.TextStyle(color=ft.colors.GREY_400, size=10)
                        ),
                        expand=1
                    ),
                    ft.Container(
                        content=ft.TextField(
                            label="Minute",
                            value=self.settings.get("minute", "0"),
                            bgcolor=ft.colors.GREY_800,
                            color=ft.colors.WHITE,
                            border_color=ft.colors.GREY_600,
                            focused_border_color=ft.colors.GREEN_400,
                            border_radius=8,
                            text_size=12,
                            text_align=ft.TextAlign.CENTER,
                            on_focus=self.show_time_picker,
                            label_style=ft.TextStyle(color=ft.colors.GREY_400, size=10)
                        ),
                        expand=1
                    )
                ], spacing=20)
            ], spacing=10),
            bgcolor=ft.colors.GREY_800,
            padding=15,
            border_radius=12,
            border=ft.border.all(1, ft.colors.GREY_700)
        )

        self.day_field = date_section.content.controls[1].controls[0].content
        self.month_field = date_section.content.controls[1].controls[1].content
        self.year_field = date_section.content.controls[1].controls[2].content
        self.hour_field = time_section.content.controls[1].controls[0].content
        self.minute_field = time_section.content.controls[1].controls[1].content

        buttons_section = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.ElevatedButton(
                        text="Login to PERSON Web",
                        icon=ft.icons.LOGIN,
                        on_click=self.open_PERSON_web,
                        style=ft.ButtonStyle(
                            bgcolor=ft.colors.CYAN_600,
                            color=ft.colors.WHITE,
                            shape=ft.RoundedRectangleBorder(radius=12),
                            elevation=5,
                            padding=ft.padding.symmetric(vertical=15, horizontal=20)
                        ),
                        width=300,
                        height=50
                    ),
                    alignment=ft.alignment.center
                ),
                ft.Row([
                    ft.Container(
                        content=ft.ElevatedButton(
                            text="Schedule",
                            icon=ft.icons.SCHEDULE,
                            on_click=self.schedule_message,
                            style=ft.ButtonStyle(
                                bgcolor=ft.colors.BLUE_600,
                                color=ft.colors.WHITE,
                                shape=ft.RoundedRectangleBorder(radius=12),
                                elevation=5,
                                padding=ft.padding.symmetric(vertical=12, horizontal=15)
                            ),
                            height=45
                        ),
                        expand=1
                    ),
                    ft.Container(
                        content=ft.ElevatedButton(
                            text="Test Send",
                            icon=ft.icons.SEND,
                            on_click=self.test_send,
                            style=ft.ButtonStyle(
                                bgcolor=ft.colors.ORANGE_600,
                                color=ft.colors.WHITE,
                                shape=ft.RoundedRectangleBorder(radius=12),
                                elevation=5,
                                padding=ft.padding.symmetric(vertical=12, horizontal=15)
                            ),
                            height=45
                        ),
                        expand=1
                    )
                ], spacing=10),
                ft.Row([
                    ft.Container(
                        content=ft.ElevatedButton(
                            text="Show History",
                            icon=ft.icons.HISTORY,
                            on_click=self.toggle_history_view,
                            style=ft.ButtonStyle(
                                bgcolor=ft.colors.PURPLE_600,
                                color=ft.colors.WHITE,
                                shape=ft.RoundedRectangleBorder(radius=12),
                                elevation=5,
                                padding=ft.padding.symmetric(vertical=12, horizontal=15)
                            ),
                            height=45
                        ),
                        expand=1
                    ),
                    ft.Container(
                        content=ft.ElevatedButton(
                            text="Save & Exit",
                            icon=ft.icons.SAVE_ALT,
                            on_click=self.save_and_exit,
                            style=ft.ButtonStyle(
                                bgcolor=ft.colors.GREEN_600,
                                color=ft.colors.WHITE,
                                shape=ft.RoundedRectangleBorder(radius=12),
                                elevation=5,
                                padding=ft.padding.symmetric(vertical=12, horizontal=15)
                            ),
                            height=45
                        ),
                        expand=1
                    )
                ], spacing=10)
            ], spacing=15),
            padding=20
        )

        self.history_container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row([
                        ft.Icon(ft.icons.HISTORY, color=ft.colors.PURPLE_400, size=20),
                        ft.Text("Message History", color=ft.colors.WHITE, weight=ft.FontWeight.W_500)
                    ], spacing=8),
                    ft.Column([], scroll=ft.ScrollMode.AUTO, height=200, spacing=5)
                ],
                spacing=10
            ),
            visible=False,
            bgcolor=ft.colors.GREY_800,
            border_radius=12,
            padding=15,
            margin=ft.margin.only(top=10, left=20, right=20, bottom=20),
            border=ft.border.all(1, ft.colors.GREY_700)
        )
        
        self.update_history_view()

        main_content = ft.Container(
            content=ft.Column([
                header,
                ft.Container(
                    content=ft.Column([
                        self.number_field,
                        self.message_field,
                        date_section,
                        time_section,
                    ], spacing=15),
                    padding=ft.padding.symmetric(horizontal=20)
                ),
                buttons_section,
                self.history_container
            ], spacing=0, scroll=ft.ScrollMode.AUTO),
            expand=True
        )

        self.page.add(main_content)
        self.page.on_resized = lambda e: self.update_responsive_layout()
        self.update_responsive_layout()

    def update_responsive_layout(self):
        window_width = self.page.window.width if self.page.window.width else 420
        
        field_width = min(350, window_width * 0.9)
        button_width = min(300, window_width * 0.8)
        
        self.number_field.width = field_width
        self.message_field.width = field_width
        
        if hasattr(self, 'history_container'):
            self.history_container.width = field_width
        
        self.page.update()

def run_scheduler(schedule_file):
    import schedule
    import pywhatkit
    import json
    import time
    import logging
    from datetime import datetime

    logging.basicConfig(
        filename="scheduler.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    def load_schedule():
        try:
            if os.path.exists(schedule_file):
                with open(schedule_file, "r") as f:
                    return json.load(f)
        except Exception as e:
            logging.error(f"Error loading schedule: {str(e)}")
        return {}

    def load_history(history_file):
        try:
            if os.path.exists(history_file):
                with open(history_file, "r") as f:
                    return json.load(f)
        except Exception as e:
            logging.error(f"Error loading history: {str(e)}")
        return []

    def send_PERSON(number, message, hour, minute):
        try:
            logging.info(f"Attempting to send message to {number} at {hour:02d}:{minute:02d}")
            pywhatkit.sendwhatmsg(number, message, hour, minute, wait_time=40, tab_close=True)
            logging.info(f"Message sent successfully to {number}")
            history_file = "send_history.json"
            history = load_history(history_file)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            history.append({
                "timestamp": timestamp,
                "number": number,
                "message": message,
                "status": "Success",
                "error": ""
            })
            with open(history_file, "w") as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            logging.error(f"Failed to send message to {number}: {str(e)}")
            history_file = "send_history.json"
            history = load_history(history_file)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            history.append({
                "timestamp": timestamp,
                "number": number,
                "message": message,
                "status": "Failed",
                "error": str(e)
            })
            with open(history_file, "w") as f:
                json.dump(history, f, indent=2)

    def check_schedule():
        schedule_data = load_schedule()
        if not schedule_data.get("active"):
            return
        try:
            year = int(schedule_data.get("year"))
            month = int(schedule_data.get("month"))
            day = int(schedule_data.get("day"))
            hour = int(schedule_data.get("hour"))
            minute = int(schedule_data.get("minute"))
            number = schedule_data.get("number")
            message = schedule_data.get("message")
            schedule_time = datetime(year, month, day, hour, minute)
            now = datetime.now()
            if now.year == year and now.month == month and now.day == day:
                schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(
                    send_PERSON, number, message, hour, minute
                )
                logging.info(f"Scheduled message for {number} at {year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}")
            if now >= schedule_time:
                schedule_data["active"] = False
                with open(schedule_file, "w") as f:
                    json.dump(schedule_data, f, indent=2)
                logging.info("Schedule deactivated after sending")
        except Exception as e:
            logging.error(f"Error in scheduler: {str(e)}")

    schedule.every(60).seconds.do(check_schedule)
    while True:
        schedule.run_pending()
        time.sleep(1)

def main(page: ft.Page):
    logging.info("Application started")
    PERSONAutomator(page)

if __name__ == "__main__":
    ft.app(target=main)