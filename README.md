# Zakaat Calculator App

A simple, user-friendly mobile application for calculating Zakaat built with Python and Kivy.

## Features

- Calculate Zakaat (2.5% of eligible assets) based on user inputs
- Input various assets: cash, savings, gold, silver, investments, etc.
- Subtract debts from eligible assets
- Save calculations for future reference
- Set reminders for annual Zakaat payments
- Educational information about Zakaat criteria and rules

## Requirements

- Python 3.6+
- Kivy 2.0.0+

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/zakaat.git
   cd zakaat
   ```

2. Install the required dependencies:
   ```
   pip install kivy
   ```

## Usage

Run the application:
```
python zakaat.py
```

## Application Structure

The application consists of five main screens:

1. **Home Screen**: Navigate to different sections of the app
2. **Calculator Screen**: Enter your assets and calculate Zakaat
   - Add cash, gold, silver, investments, and other assets
   - Subtract eligible debts
   - View your Zakaat obligation (2.5% of eligible assets)
3. **Info Screen**: Learn about Zakaat rules and eligibility
4. **History Screen**: View and manage past calculations
5. **Reminders Screen**: Set up reminders for annual Zakaat payments

## Data Storage

The application uses Kivy's JsonStore for persistent storage:
- `zakaat_history.json`: Stores your calculation history
- `zakaat_reminders.json`: Stores your Zakaat payment reminders

## Nisab Calculation

The app uses the following Nisab thresholds:
- Gold: 87.48 grams
- Silver: 612.36 grams

Zakaat is calculated at 2.5% of eligible assets when they exceed the lower of these two thresholds.

## About Zakaat

Zakaat is one of the five pillars of Islam, requiring eligible Muslims to give 2.5% of their qualifying wealth to specific categories of recipients. The app helps determine if you've reached the Nisab threshold (minimum amount) and calculates the exact amount due.
