# Personal Finance Tracker - Nepal Edition 🏦🇳🇵

A comprehensive personal finance management application built specifically for Nepal, with all amounts in Nepali Rupees (NPR). This application demonstrates advanced programming concepts, data analysis, and visualization capabilities tailored for Nepali users.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![SQLite](https://img.shields.io/badge/Database-SQLite-green)
![Pandas](https://img.shields.io/badge/Data-Pandas-yellow)
![Matplotlib](https://img.shields.io/badge/Visualization-Matplotlib-red)

## 🌟 Features

### Core Functionality
- **Transaction Management**: Add, view, and categorize income and expenses
- **Budget Tracking**: Set monthly budgets and track spending against limits
- **Data Visualization**: Interactive charts and graphs for financial insights
- **Financial Analytics**: Comprehensive reporting and trend analysis
- **Data Export**: Export financial data to CSV format
- **Currency Conversion**: Real-time currency conversion using API integration

### Technical Highlights
- **Object-Oriented Design**: Clean, modular architecture with separation of concerns
- **Database Integration**: SQLite for persistent data storage
- **Data Analysis**: Pandas for efficient data manipulation and analysis
- **Visualization**: Professional charts using Matplotlib and Seaborn
- **API Integration**: Real-time currency conversion
- **Error Handling**: Comprehensive logging and exception handling
- **Type Hints**: Modern Python practices with type annotations
- **Documentation**: Extensive docstrings and comments

## 🛠️ Technologies Used

| Category | Technology | Purpose |
|----------|------------|----------|
| **Language** | Python 3.8+ | Core application development |
| **Database** | SQLite | Data persistence and storage |
| **Data Analysis** | Pandas | Data manipulation and analysis |
| **Visualization** | Matplotlib, Seaborn | Charts and graphs generation |
| **HTTP Requests** | Requests | API integration for currency conversion |
| **Date/Time** | datetime, python-dateutil | Date handling and calculations |
| **Type Safety** | typing, dataclasses | Type hints and data structures |
| **Logging** | logging | Application monitoring and debugging |

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd PersonalFinanceTracker
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv finance_env
   
   # Windows
   finance_env\Scripts\activate
   
   # macOS/Linux
   source finance_env/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Usage

### Easy Start - Use the Launcher

```bash
python launcher.py
```

This will start the Personal Finance Tracker where you can:
- 💰 Add your real income and expenses in NPR
- 🎯 Set and track personal budgets
- 📈 Generate reports based on your actual data
- 💡 Use Nepal-specific categories (Festival/Religious, Remittance, etc.)
- 📊 Create beautiful visualizations of your finances

### Alternative - Direct Access

```bash
python interactive_finance_tracker.py
```

### Using as a Library

```python
from finance_tracker import FinanceTracker


### Class Structure

```
FinanceTracker (Main Controller)
├── DatabaseManager (Data Persistence)
├── FinanceAnalyzer (Analytics & Visualization)
└── CurrencyConverter (API Integration)

Transaction (Data Model)
```

### Key Classes

- **`FinanceTracker`**: Main application controller
- **`DatabaseManager`**: Handles SQLite database operations
- **`FinanceAnalyzer`**: Generates reports and visualizations
- **`CurrencyConverter`**: Handles currency conversion via API
- **`Transaction`**: Data class for transaction objects

## 📈 Generated Visualizations

The application generates professional charts including:

1. **Expense Breakdown Pie Chart**: Shows spending distribution by category
2. **Monthly Trends Line Chart**: Displays income vs expenses over time
3. **Budget Progress Charts**: Visual budget tracking

## 🔧 Configuration

### Database
- **Default**: `finance_tracker.db` (SQLite)
- **Location**: Same directory as the script
- **Schema**: Automatically created on first run

### Logging
- **Log File**: `finance_tracker.log`
- **Level**: INFO
- **Format**: Timestamp, Level, Message

## 🧪 Testing

The project includes a comprehensive demo that tests all functionality:

```bash
python finance_tracker.py
```

For unit testing (if implemented):
```bash
pytest tests/
```

## 📝 Code Quality

This project demonstrates:

- **Clean Code**: Readable, well-structured code with meaningful names
- **Documentation**: Comprehensive docstrings and comments
- **Error Handling**: Proper exception handling and logging
- **Type Safety**: Type hints throughout the codebase
- **Separation of Concerns**: Each class has a single responsibility
- **DRY Principle**: No code duplication
- **SOLID Principles**: Object-oriented design best practices

## 🚀 Future Enhancements

Potential improvements for portfolio expansion:

- [ ] Web interface using Flask/Django
- [ ] Mobile app version
- [ ] Investment tracking
- [ ] Multiple account support
- [ ] Automated transaction import
- [ ] Machine learning for expense categorization
- [ ] Goal setting and tracking
- [ ] Receipt scanning and OCR
- [ ] Multi-user support
- [ ] Advanced reporting dashboard

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 👤 Author

**Saksham Lamsal**
- Portfolio: https://www.sakshamlamsal.com.np/
- GitHub: https://github.com/Saksham1000
- Linkedin: https://www.linkedin.com/in/saksham-lamsal-695617238/
- Email: sakshamlamsal99@gmail.com

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## ⭐ Show Your Support

Give a ⭐ if this project helped you!

---



