# Attendbot 🤖

![Attendbot Logo](https://via.placeholder.com/150)

---

## What is Attendbot?

Attendbot is a powerful automation tool designed to simplify the process of submitting manual attendance in the Capgemini portal. Powered by Selenium and Beautiful Soup, Attendbot operates seamlessly in headless mode, providing a hassle-free experience for users.

---

## Features

- **Automated Attendance Submission:** Say goodbye to manual attendance submissions. Attendbot automates the process for you.
- **Headless Mode:** Operates in headless mode by default, ensuring smooth execution without displaying the browser window.
- **Logging and Reporting:** Generates detailed logs and reports of attendance marked, enabling users to verify and troubleshoot any issues.
- **Customizable:** Users can specify the month for which attendance needs to be applied, providing flexibility and convenience.
- **Interactive Mode:** Optionally, users can run the program in interactive mode (-i flag) to view the browser window and interact with it directly.

---

## Installation (Windows)

### Requirements
- Python 3.10 or higher

### Instructions
1. Open Command Prompt.
2. Navigate to the directory containing the Attendbot package.
3. Run the following command to install Attendbot:
    ```bash
    pip install Attendbot
    ```

---

## Usage

### Running the Program
1. Open Command Prompt.
2. Navigate to the directory containing the Attendbot package.
3. Run the following command to mark attendance for the previous month:
    ```bash
    py -m Attendbot.mark
    ```

### Interactive Mode
To run the program in interactive mode (displaying the browser window), use the -i flag:
```bash
py -m Attendbot.mark -i
```