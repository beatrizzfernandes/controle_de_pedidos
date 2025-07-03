# 🧾 Order Management System with WhatsApp Notification

This project is an order management system built in Python with a modern interface using [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter). It allows you to register, view, and edit orders, and automatically sends WhatsApp messages to customers when an order is created or its status is updated.

---

## 📸 Screenshots

<table>
  <tr>
    <td>
      <img src="https://github.com/user-attachments/assets/4e5fd56f-f9ed-442e-b28d-4fdf9802d13c" width="300"/>
    </td>
    <td>
      <img src="https://github.com/user-attachments/assets/c412b515-db66-4303-a093-e8abba0164cf" width="300"/>
    </td>
  </tr>
  <tr>
    <td>
      <img src="https://github.com/user-attachments/assets/5534b1bc-f993-46c4-9365-c3fdecf6ca2f" width="300"/>
    </td>
    <td>
      <img src="https://github.com/user-attachments/assets/75a8b6ec-af81-4420-90d1-b113254a8b5f" width="300"/>
    </td>
  </tr>
</table>

---

## 🛠 Technologies Used

- Python 3.10+
- CustomTkinter
- pandas
- openpyxl
- requests
- External WhatsApp API (Evolution API)
- tkinter / ttk (interface foundation)

---

## ✨ Features

- ✅ Order registration with field validation
- 📦 View, edit, and delete orders stored in Excel
- 🟨 Dashboard with:
  - Total orders of the day
  - Total sales value
  - Most sold product
- 📤 Automatic WhatsApp notifications to customers:
  - When an order is registered
  - When the order status is updated
- 📈 Daily report generation in Excel and email sending
- ⚙️ `config.json` file centralizes all sensitive configurations

---

## 📂 Project Structure


```
controle-pedidos/
│
├── interface.py           # Main application file
├── config.json            # API and email configuration
├── produtos.json          # Product list and prices
├── pedidos.xlsx           # Order database
└── relatorios/            # Automatically generated reports
```

---

## 🚀 Possible Future Improvements

- Integration with a real database (SQLite or PostgreSQL)
- Web interface using Flask or Django
- PDF report module
- Dashboard with charts
- Simple chatbot to check order status
- Automatic reminders for pending orders after X hours
- Discount or coupon system

---

## 👤 Author

Created by [![GitHub](https://img.shields.io/badge/GitHub-@beatrizzfernandes-000?logo=github)](https://github.com/beatrizzfernandes)

🎓 Technical degree in Software Development and pursuing a degree in Systems Analysis and Development

⚙️ Experience with Python, automation, RPA, APIs, bots, and UI development

---

**⭐ If this project helped you or caught your attention, don’t forget to give it a star!**




