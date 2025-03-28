<div align="center">
  <a href="https://github.com/alexdrumi/webserv">
    <img src="data/www/webserver.jpg" alt="MNE EEG Logo" width="550" height="250">
  </a>
</div>


# Habit Tracker CLI
A Habit Tracker CLI application built with Django that leverages OOP and design pattern principles to manage users, habits, goals, progress, and reminders.


<br>

## Table of Contents
* [General Info](#general-information)
* [Technologies Used](#technologies-used)
* [Features](#features)
* [Screenshots](#screenshots)
* [Setup](#setup)
* [Usage](#usage)


## General Information
Habit Tracker CLI is a command-line application that helps users monitor and improve their daily habits. It uses Django as its backend framework and implements object-oriented design patterns—such as the repository, service, and controller patterns—to ensure the code is modular, testable, and maintainable. The project allows you to:<br>

- Create, update, and delete user accounts.<br>
- Set up daily or weekly habits..<br>
- Define goals for each habit.
- Track progress with timestamps and streak calculations.
- Generate reminders and perform basic analytics.

.<br>


## Technologies Used
- Python 3.8+ – Primary language for the CLI and business logic.
- Django – Backend framework for managing models and migrations.
- MySQL/MariaDB – Database engine.
- Click - For building the command-line interface.
- Pytest - Unit testing framework for all repositories/services.
  


## Features
- User Management: Create, update, delete, and validate users.
- Habit Management: Add and modify daily/weekly habits.
- Goal Setting: Define goals for each habit.
- Progress Tracking: Record progress entries with timestamps and compute streaks.
- Reminders & Analytics: Set up reminders and view habit analytics.
- CLI Interface: Interact with the application through a command-line interface.
- All interaction with MariaDB are via repositories, implemented with raw SQL queries.



## Screenshots
![Example screenshot](./data/www/screenshot.png)



## Setup
Requirements are:
- Docker
- Python 3.8

### Installation
1. **Clone the repository:**
   ```bash
   git clone git@github.com:alexdrumi/habit_tracker.git
   cd habit_tracker

2. **Change the environment variable name. (optional: alter usernames, passwords etc):**
   ```bash
   mv .env_example .env  


2. **Build containers and packages:**
   ```bash
   make build
  
2. **Run containers:**
   ```bash
   make up
2. **Setup virtual environment:**
   ```bash
   make setup_env
2. **Migrate database:**
   ```bash
   make migrate_local
2. **Enter virtual environment:**
   ```bash
   source venv/bin/activate



## Usage
2. **Run the Habit Tracker CLI by executing the main function (inside virtualenv):**
   ```bash
   python main.py

2. **To seed the database with sample data, use:**
   ```bash
   python main.py --seed


## Sources
