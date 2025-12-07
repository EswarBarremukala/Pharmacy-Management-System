# 💊 Pharmacy Management System (Flask & SQL)

## 📌 Project Overview
This is a **Web-Based Inventory Management System** designed for pharmacies to efficiently track stock, monitor expiry dates, and maintain audit logs. The application is built using **Python (Flask)** for the backend and **SQLite** for data storage. It replaces manual register entries with an automated system that calculates "Days Remaining" for every medicine in real-time and provides visual alerts for expiring stock.

## 🚀 Features

* **Smart Inventory Tracking:** Add medicines with details like Name, Batch Number, Quantity, and Expiry Date. The system prevents duplicate entries for the same Batch ID.
* **Real-time Expiry Calculation:** Automatically calculates and displays the **"Days Remaining"** for every batch relative to the current date.
* **Visual Status Indicators:** Uses color-coded rows to highlight stock status:
    * 🔴 **Red:** Expired
    * 🟠 **Orange:** Warning (< 50 Days left)
    * 🟢 **Green:** Safe
* **Risk Evaluation Log:** A "One-Click Evaluation" feature that scans the entire inventory and saves risky items to a permanent **History Table** for future reference (auditing).
* **Search & Filter:** Instantly search for medicines by Name or Batch Number.
* **Bulk Maintenance:** A "Delete Expired" feature to safely remove all expired stock from the active inventory in one click.

## 🛠️ Tech Stack

* **Frontend:** HTML5, CSS3 (Embedded Styles)
* **Backend:** Python 3.x, Flask Web Framework
* **Database:** SQLite (Relational Database)
* **Logic:** Python `datetime` module for date arithmetic

## 📂 Project Structure

```text
PharmacyProject/
│
├── app.py               # Main Flask application (Backend & Routes)
├── pharmacy.db          # SQLite Database (Auto-generated)
├── requirements.txt     # List of dependencies
└── templates/
    └── index.html       # User Interface (HTML & CSS)




<img width="155" height="148" alt="image" src="https://github.com/user-attachments/assets/b8b9d42c-562f-400a-a89a-072f32a47e4f" />

