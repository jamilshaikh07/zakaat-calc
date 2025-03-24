"""
Zakaat Calculator Module

A simple mobile application to calculate Zakaat based on user's assets.
"""
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.storage.jsonstore import JsonStore
from kivy.clock import Clock
from kivy.utils import platform
from datetime import datetime, timedelta
import os

# Constants
NISAB_GOLD = 87.48  # Nisab threshold in grams of gold
NISAB_SILVER = 612.36  # Nisab threshold in grams of silver
ZAKAAT_RATE = 0.025  # 2.5%

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Title
        title = Label(
            text='Zakaat Calculator',
            font_size=24,
            size_hint_y=None,
            height=50
        )
        layout.add_widget(title)
        
        # Buttons
        calc_button = Button(
            text='Calculate Zakaat',
            size_hint_y=None,
            height=50
        )
        calc_button.bind(on_press=self.go_to_calculator)
        
        info_button = Button(
            text='About Zakaat',
            size_hint_y=None,
            height=50
        )
        info_button.bind(on_press=self.go_to_info)
        
        history_button = Button(
            text='Saved Calculations',
            size_hint_y=None,
            height=50
        )
        history_button.bind(on_press=self.go_to_history)
        
        reminder_button = Button(
            text='Set Reminders',
            size_hint_y=None,
            height=50
        )
        reminder_button.bind(on_press=self.go_to_reminders)
        
        layout.add_widget(calc_button)
        layout.add_widget(info_button)
        layout.add_widget(history_button)
        layout.add_widget(reminder_button)
        
        self.add_widget(layout)
    
    def go_to_calculator(self, instance):
        self.manager.current = 'calculator'
    
    def go_to_info(self, instance):
        self.manager.current = 'info'
    
    def go_to_history(self, instance):
        self.manager.current = 'history'
    
    def go_to_reminders(self, instance):
        self.manager.current = 'reminders'

class CalculatorScreen(Screen):
    def __init__(self, **kwargs):
        super(CalculatorScreen, self).__init__(**kwargs)
        self.asset_inputs = {}
        
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Title and back button
        header = BoxLayout(size_hint_y=None, height=50)
        back_button = Button(text='Back', size_hint_x=None, width=100)
        back_button.bind(on_press=self.go_back)
        title = Label(text='Calculate Your Zakaat')
        
        header.add_widget(back_button)
        header.add_widget(title)
        main_layout.add_widget(header)
        
        # Scrollable form
        scroll_view = ScrollView()
        form_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        form_layout.bind(minimum_height=form_layout.setter('height'))
        
        # Asset inputs
        assets = [
            ('cash', 'Cash on Hand'),
            ('bank_balance', 'Bank Balance'),
            ('gold', 'Gold (grams)'),
            ('silver', 'Silver (grams)'),
            ('investments', 'Investments'),
            ('business_assets', 'Business Assets'),
            ('rental_income', 'Rental Income'),
            ('other_assets', 'Other Assets'),
            ('debts', 'Debts (to be subtracted)')
        ]
        
        for asset_id, asset_name in assets:
            asset_layout = BoxLayout(size_hint_y=None, height=50)
            asset_label = Label(text=asset_name, size_hint_x=0.4)
            asset_input = TextInput(
                hint_text='0.00',
                input_filter='float',
                multiline=False,
                size_hint_x=0.6
            )
            self.asset_inputs[asset_id] = asset_input
            
            asset_layout.add_widget(asset_label)
            asset_layout.add_widget(asset_input)
            form_layout.add_widget(asset_layout)
        
        # Calculate button
        calculate_button = Button(
            text='Calculate Zakaat',
            size_hint_y=None,
            height=50
        )
        calculate_button.bind(on_press=self.calculate_zakaat)
        form_layout.add_widget(calculate_button)
        
        # Save button
        save_button = Button(
            text='Save Calculation',
            size_hint_y=None,
            height=50
        )
        save_button.bind(on_press=self.save_calculation)
        form_layout.add_widget(save_button)
        
        # Results label
        self.result_label = Label(
            text='Enter your assets to calculate Zakaat',
            size_hint_y=None,
            height=100,
            text_size=(400, None),
            halign='center'
        )
        form_layout.add_widget(self.result_label)
        
        scroll_view.add_widget(form_layout)
        main_layout.add_widget(scroll_view)
        
        self.add_widget(main_layout)
    
    def go_back(self, instance):
        self.manager.current = 'home'
    
    def calculate_zakaat(self, instance):
        try:
            # Get values from inputs
            assets = {}
            for asset_id, input_widget in self.asset_inputs.items():
                try:
                    value = float(input_widget.text) if input_widget.text else 0
                    assets[asset_id] = value
                except ValueError:
                    assets[asset_id] = 0
            
            # Calculate total assets
            gold_value = assets.get('gold', 0)
            silver_value = assets.get('silver', 0)
            
            total_assets = (
                assets.get('cash', 0) +
                assets.get('bank_balance', 0) +
                assets.get('investments', 0) +
                assets.get('business_assets', 0) +
                assets.get('rental_income', 0) +
                assets.get('other_assets', 0)
            )
            
            # Subtract debts
            net_assets = total_assets - assets.get('debts', 0)
            
            # Check if assets meet Nisab threshold
            # For simplicity, we're using a fixed gold price. In a real app, you'd fetch current prices.
            gold_price_per_gram = 60  # Example price in USD
            silver_price_per_gram = 0.8  # Example price in USD
            
            nisab_gold_value = NISAB_GOLD * gold_price_per_gram
            nisab_silver_value = NISAB_SILVER * silver_price_per_gram
            
            # Use the lower of the two Nisab values
            nisab_threshold = min(nisab_gold_value, nisab_silver_value)
            
            # Add value of gold and silver
            gold_total_value = gold_value * gold_price_per_gram
            silver_total_value = silver_value * silver_price_per_gram
            
            net_assets += gold_total_value + silver_total_value
            
            # Calculate Zakaat if above Nisab
            if net_assets >= nisab_threshold:
                zakaat_amount = net_assets * ZAKAAT_RATE
                self.result_label.text = f"Your total Zakaat is: ${zakaat_amount:.2f}\n" \
                                        f"Based on net assets of: ${net_assets:.2f}"
            else:
                self.result_label.text = f"Your net assets (${net_assets:.2f}) are below " \
                                        f"the Nisab threshold (${nisab_threshold:.2f}).\n" \
                                        f"No Zakaat is due."
            
            # Store calculation for potential saving
            self.current_calculation = {
                'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'assets': assets,
                'net_assets': net_assets,
                'zakaat_amount': zakaat_amount if net_assets >= nisab_threshold else 0,
                'nisab_threshold': nisab_threshold
            }
            
        except Exception as e:
            self.result_label.text = f"Error in calculation: {str(e)}"
    
    def save_calculation(self, instance):
        if not hasattr(self, 'current_calculation'):
            popup = Popup(
                title='Error',
                content=Label(text='Please calculate Zakaat first'),
                size_hint=(0.8, 0.3)
            )
            popup.open()
            return
        
        try:
            # Get the data store
            store = JsonStore('zakaat_history.json')
            
            # Generate a unique key based on timestamp
            key = f"calc_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Save the calculation
            store.put(key, **self.current_calculation)
            
            popup = Popup(
                title='Success',
                content=Label(text='Calculation saved successfully'),
                size_hint=(0.8, 0.3)
            )
            popup.open()
            
        except Exception as e:
            popup = Popup(
                title='Error',
                content=Label(text=f'Failed to save: {str(e)}'),
                size_hint=(0.8, 0.3)
            )
            popup.open()

class InfoScreen(Screen):
    def __init__(self, **kwargs):
        super(InfoScreen, self).__init__(**kwargs)
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Title and back button
        header = BoxLayout(size_hint_y=None, height=50)
        back_button = Button(text='Back', size_hint_x=None, width=100)
        back_button.bind(on_press=self.go_back)
        title = Label(text='About Zakaat')
        
        header.add_widget(back_button)
        header.add_widget(title)
        main_layout.add_widget(header)
        
        # Scrollable content
        scroll_view = ScrollView()
        content_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        content_layout.bind(minimum_height=content_layout.setter('height'))
        
        zakaat_info = """
Zakaat is one of the Five Pillars of Islam and is a form of obligatory charity.

Key points about Zakaat:

1. Who must pay:
   - Adult Muslims of sound mind
   - Who possess wealth above the Nisab threshold
   - Who have had this wealth for one lunar year (Hawl)

2. Nisab threshold:
   - Equivalent to 87.48 grams of gold OR
   - Equivalent to 612.36 grams of silver
   - The lower of these two values is typically used

3. Rate of Zakaat:
   - 2.5% of eligible assets

4. Assets subject to Zakaat:
   - Cash and bank balances
   - Gold and silver (including jewelry)
   - Investments and stocks
   - Business inventory and merchandise
   - Rental income
   - Agricultural produce (different rates apply)
   - Livestock (different rates apply)

5. Assets exempt from Zakaat:
   - Personal items (clothing, household furniture)
   - Primary residence
   - Vehicles for personal use
   - Debts (can be subtracted from assets)

6. Recipients of Zakaat:
   - The poor and needy
   - Those employed to collect Zakaat
   - New converts to Islam
   - Those in debt
   - Travelers in need
   - Those in the cause of Allah
   - Those in bondage or captivity

Zakaat purifies wealth and helps create a more equitable society by redistributing wealth to those in need.
        """
        
        info_label = Label(
            text=zakaat_info,
            text_size=(400, None),
            size_hint_y=None,
            halign='left',
            valign='top'
        )
        info_label.bind(texture_size=info_label.setter('size'))
        
        content_layout.add_widget(info_label)
        scroll_view.add_widget(content_layout)
        main_layout.add_widget(scroll_view)
        
        self.add_widget(main_layout)
    
    def go_back(self, instance):
        self.manager.current = 'home'

class HistoryScreen(Screen):
    def __init__(self, **kwargs):
        super(HistoryScreen, self).__init__(**kwargs)
        self.main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Title and back button
        header = BoxLayout(size_hint_y=None, height=50)
        back_button = Button(text='Back', size_hint_x=None, width=100)
        back_button.bind(on_press=self.go_back)
        title = Label(text='Saved Calculations')
        
        header.add_widget(back_button)
        header.add_widget(title)
        self.main_layout.add_widget(header)
        
        # Content will be loaded when the screen is entered
        self.add_widget(self.main_layout)
    
    def on_enter(self):
        # Clear previous content
        if len(self.main_layout.children) > 1:
            self.main_layout.remove_widget(self.main_layout.children[0])
        
        # Create scrollable content
        scroll_view = ScrollView()
        content_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        content_layout.bind(minimum_height=content_layout.setter('height'))
        
        try:
            # Load saved calculations
            if os.path.exists('zakaat_history.json'):
                store = JsonStore('zakaat_history.json')
                
                if not store.keys():
                    no_data_label = Label(
                        text='No saved calculations found',
                        size_hint_y=None,
                        height=50
                    )
                    content_layout.add_widget(no_data_label)
                else:
                    # Display each saved calculation
                    for key in store.keys():
                        calc = store.get(key)
                        
                        calc_layout = BoxLayout(
                            orientation='vertical',
                            size_hint_y=None,
                            height=150,
                            padding=10,
                            spacing=5
                        )
                        
                        date_label = Label(
                            text=f"Date: {calc.get('date', 'Unknown')}",
                            size_hint_y=None,
                            height=30,
                            halign='left'
                        )
                        
                        assets_label = Label(
                            text=f"Net Assets: ${calc.get('net_assets', 0):.2f}",
                            size_hint_y=None,
                            height=30,
                            halign='left'
                        )
                        
                        zakaat_label = Label(
                            text=f"Zakaat Amount: ${calc.get('zakaat_amount', 0):.2f}",
                            size_hint_y=None,
                            height=30,
                            halign='left'
                        )
                        
                        # Delete button
                        delete_button = Button(
                            text='Delete',
                            size_hint_y=None,
                            height=30
                        )
                        delete_button.bind(on_press=lambda btn, k=key: self.delete_calculation(k))
                        
                        calc_layout.add_widget(date_label)
                        calc_layout.add_widget(assets_label)
                        calc_layout.add_widget(zakaat_label)
                        calc_layout.add_widget(delete_button)
                        
                        # Add a separator
                        separator = BoxLayout(size_hint_y=None, height=1)
                        
                        content_layout.add_widget(calc_layout)
                        content_layout.add_widget(separator)
            else:
                no_data_label = Label(
                    text='No saved calculations found',
                    size_hint_y=None,
                    height=50
                )
                content_layout.add_widget(no_data_label)
                
        except Exception as e:
            error_label = Label(
                text=f'Error loading saved calculations: {str(e)}',
                size_hint_y=None,
                height=50
            )
            content_layout.add_widget(error_label)
        
        scroll_view.add_widget(content_layout)
        self.main_layout.add_widget(scroll_view)
    
    def go_back(self, instance):
        self.manager.current = 'home'
    
    def delete_calculation(self, key):
        try:
            store = JsonStore('zakaat_history.json')
            store.delete(key)
            
            # Refresh the screen
            self.on_enter()
            
        except Exception as e:
            popup = Popup(
                title='Error',
                content=Label(text=f'Failed to delete: {str(e)}'),
                size_hint=(0.8, 0.3)
            )
            popup.open()

class RemindersScreen(Screen):
    def __init__(self, **kwargs):
        super(RemindersScreen, self).__init__(**kwargs)
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Title and back button
        header = BoxLayout(size_hint_y=None, height=50)
        back_button = Button(text='Back', size_hint_x=None, width=100)
        back_button.bind(on_press=self.go_back)
        title = Label(text='Zakaat Reminders')
        
        header.add_widget(back_button)
        header.add_widget(title)
        main_layout.add_widget(header)
        
        # Reminder form
        form_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Reminder type
        type_layout = BoxLayout(size_hint_y=None, height=50)
        type_label = Label(text='Reminder Type:', size_hint_x=0.4)
        self.reminder_type = Spinner(
            text='Annual',
            values=('Annual', 'Monthly', 'Custom'),
            size_hint_x=0.6
        )
        type_layout.add_widget(type_label)
        type_layout.add_widget(self.reminder_type)
        
        # Date selection (simplified for this example)
        date_layout = BoxLayout(size_hint_y=None, height=50)
        date_label = Label(text='Start Date:', size_hint_x=0.4)
        self.date_input = TextInput(
            hint_text='YYYY-MM-DD',
            multiline=False,
            size_hint_x=0.6
        )
        date_layout.add_widget(date_label)
        date_layout.add_widget(self.date_input)
        
        # Note
        note_layout = BoxLayout(size_hint_y=None, height=50)
        note_label = Label(text='Note:', size_hint_x=0.4)
        self.note_input = TextInput(
            hint_text='Optional note',
            multiline=False,
            size_hint_x=0.6
        )
        note_layout.add_widget(note_label)
        note_layout.add_widget(self.note_input)
        
        # Set reminder button
        set_button = Button(
            text='Set Reminder',
            size_hint_y=None,
            height=50
        )
        set_button.bind(on_press=self.set_reminder)
        
        form_layout.add_widget(type_layout)
        form_layout.add_widget(date_layout)
        form_layout.add_widget(note_layout)
        form_layout.add_widget(set_button)
        
        # Existing reminders section
        self.reminders_layout = BoxLayout(orientation='vertical', spacing=10)
        reminders_label = Label(
            text='Your Reminders:',
            size_hint_y=None,
            height=30
        )
        self.reminders_layout.add_widget(reminders_label)
        
        main_layout.add_widget(form_layout)
        main_layout.add_widget(self.reminders_layout)
        
        self.add_widget(main_layout)
    
    def on_enter(self):
        self.load_reminders()
    
    def go_back(self, instance):
        self.manager.current = 'home'
    
    def set_reminder(self, instance):
        try:
            # Validate date
            date_str = self.date_input.text
            try:
                start_date = datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                start_date = datetime.now()
            
            # Get reminder type and note
            reminder_type = self.reminder_type.text
            note = self.note_input.text
            
            # Calculate next reminder date based on type
            if reminder_type == 'Annual':
                next_date = start_date + timedelta(days=365)
            elif reminder_type == 'Monthly':
                next_date = start_date + timedelta(days=30)
            else:  # Custom
                next_date = start_date + timedelta(days=7)  # Default to weekly
            
            # Save reminder
            store = JsonStore('zakaat_reminders.json')
            key = f"reminder_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            store.put(key, 
                     type=reminder_type,
                     start_date=start_date.strftime('%Y-%m-%d'),
                     next_date=next_date.strftime('%Y-%m-%d'),
                     note=note)
            
            # Refresh reminders list
            self.load_reminders()
            
            # Clear inputs
            self.date_input.text = ''
            self.note_input.text = ''
            
            # Show confirmation
            popup = Popup(
                title='Success',
                content=Label(text='Reminder set successfully'),
                size_hint=(0.8, 0.3)
            )
            popup.open()
            
        except Exception as e:
            popup = Popup(
                title='Error',
                content=Label(text=f'Failed to set reminder: {str(e)}'),
                size_hint=(0.8, 0.3)
            )
            popup.open()
    
    def load_reminders(self):
        # Clear previous reminders
        for child in list(self.reminders_layout.children)[:-1]:  # Keep the title
            self.reminders_layout.remove_widget(child)
        
        try:
            if os.path.exists('zakaat_reminders.json'):
                store = JsonStore('zakaat_reminders.json')
                
                if not store.keys():
                    no_data_label = Label(
                        text='No reminders set',
                        size_hint_y=None,
                        height=30
                    )
                    self.reminders_layout.add_widget(no_data_label)
                else:
                    # Display each reminder
                    for key in store.keys():
                        reminder = store.get(key)
                        
                        reminder_layout = BoxLayout(
                            orientation='horizontal',
                            size_hint_y=None,
                            height=50
                        )
                        
                        info_text = f"{reminder.get('type', 'Unknown')} - " \
                                   f"Next: {reminder.get('next_date', 'Unknown')} - " \
                                   f"{reminder.get('note', '')}"
                        
                        info_label = Label(
                            text=info_text,
                            size_hint_x=0.8
                        )
                        
                        delete_button = Button(
                            text='Delete',
                            size_hint_x=0.2
                        )
                        delete_button.bind(on_press=lambda btn, k=key: self.delete_reminder(k))
                        
                        reminder_layout.add_widget(info_label)
                        reminder_layout.add_widget(delete_button)
                        
                        self.reminders_layout.add_widget(reminder_layout)
            else:
                no_data_label = Label(
                    text='No reminders set',
                    size_hint_y=None,
                    height=30
                )
                self.reminders_layout.add_widget(no_data_label)
                
        except Exception as e:
            error_label = Label(
                text=f'Error loading reminders: {str(e)}',
                size_hint_y=None,
                height=30
            )
            self.reminders_layout.add_widget(error_label)
    
    def delete_reminder(self, key):
        try:
            store = JsonStore('zakaat_reminders.json')
            store.delete(key)
            
            # Refresh the reminders
            self.load_reminders()
            
        except Exception as e:
            popup = Popup(
                title='Error',
                content=Label(text=f'Failed to delete reminder: {str(e)}'),
                size_hint=(0.8, 0.3)
            )
            popup.open()

class ZakaatApp(App):
    def build(self):
        # Create screen manager
        sm = ScreenManager()
        
        # Add screens
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(CalculatorScreen(name='calculator'))
        sm.add_widget(InfoScreen(name='info'))
        sm.add_widget(HistoryScreen(name='history'))
        sm.add_widget(RemindersScreen(name='reminders'))
        
        # Check for reminders on startup
        Clock.schedule_once(self.check_reminders, 5)
        
        return sm
    
    def check_reminders(self, dt):
        try:
            if os.path.exists('zakaat_reminders.json'):
                store = JsonStore('zakaat_reminders.json')
                today = datetime.now().strftime('%Y-%m-%d')
                
                for key in store.keys():
                    reminder = store.get(key)
                    next_date = reminder.get('next_date')
                    
                    if next_date == today:
                        # Show notification
                        note = reminder.get('note', '')
                        message = f"Zakaat Reminder: {note}" if note else "Zakaat Reminder"
                        
                        popup = Popup(
                            title='Zakaat Reminder',
                            content=Label(text=message),
                            size_hint=(0.8, 0.3)
                        )
                        popup.open()
                        
                        # Update next reminder date based on type
                        reminder_type = reminder.get('type')
                        current_date = datetime.strptime(next_date, '%Y-%m-%d')
                        
                        if reminder_type == 'Annual':
                            new_date = current_date + timedelta(days=365)
                        elif reminder_type == 'Monthly':
                            new_date = current_date + timedelta(days=30)
                        else:  # Custom
                            new_date = current_date + timedelta(days=7)
                        
                        # Update the reminder
                        store.put(key,
                                 type=reminder.get('type'),
                                 start_date=reminder.get('start_date'),
                                 next_date=new_date.strftime('%Y-%m-%d'),
                                 note=reminder.get('note'))
        except Exception:
            # Silently fail for reminders check
            pass

if __name__ == '__main__':
    ZakaatApp().run()
