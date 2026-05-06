import sqlite3
from tkinter import *
from tkinter import ttk, messagebox
from datetime import datetime

class BudgetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Мой бюджет - Учёт доходов и расходов")
        self.root.geometry("900x600")
        self.root.resizable(True, True)
        
        # Настройка минимального размера окна
        self.root.minsize(800, 600)
        
        # Создание базы данных
        self.init_database()
        
        # Текущий баланс
        self.current_balance = self.get_current_balance()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Загрузка истории операций
        self.load_transactions()
    
    def init_database(self):
        #Инициализация базы данных SQLite
        self.conn = sqlite3.connect('budget.db')
        self.cursor = self.conn.cursor()
        
        # Создание таблицы для транзакций
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                comment TEXT,
                date TEXT NOT NULL
            )
        ''')
        self.conn.commit()
    
    def get_current_balance(self):
        #Расчёт текущего баланса из базы данных
        # Сумма всех доходов
        self.cursor.execute('SELECT SUM(amount) FROM transactions WHERE type = "Доход"')
        income_total = self.cursor.fetchone()[0] or 0
        
        # Сумма всех расходов
        self.cursor.execute('SELECT SUM(amount) FROM transactions WHERE type = "Расход"')
        expense_total = self.cursor.fetchone()[0] or 0
        
        return income_total - expense_total
    
    def update_balance_display(self):
        #Обновление отображения текущего баланса
        self.balance_label.config(text=f"Текущий баланс: {self.current_balance:.2f} ₽")
        
        # Визуальное выделение баланса
        if self.current_balance >= 0:
            self.balance_frame.config(bg="#90EE90")  # Зелёный для положительного баланса
        else:
            self.balance_frame.config(bg="#FFB6C1")  # Красный для отрицательного
    
    def create_widgets(self):
        #Создание всех элементов интерфейса
        
        # Верхняя панель с балансом
        self.balance_frame = Frame(self.root, bg="#90EE90", height=80)
        self.balance_frame.pack(fill=X, padx=10, pady=10)
        self.balance_frame.pack_propagate(False)
        
        self.balance_label = Label(
            self.balance_frame, 
            text=f"Текущий баланс: {self.current_balance:.2f} ₽",
            font=("Arial", 20, "bold"),
            bg=self.balance_frame.cget("bg")
        )
        self.balance_label.pack(expand=True)
        
        # Основная панель с формой добавления
        input_frame = LabelFrame(self.root, text="Добавить операцию", font=("Arial", 12, "bold"))
        input_frame.pack(fill=X, padx=10, pady=10)
        
        # Поле для суммы
        Label(input_frame, text="Сумма:").grid(row=0, column=0, padx=10, pady=10, sticky=W)
        self.amount_entry = Entry(input_frame, width=20, font=("Arial", 11))
        self.amount_entry.grid(row=0, column=1, padx=10, pady=10)
        
        # Поле для комментария
        Label(input_frame, text="Комментарий:").grid(row=0, column=2, padx=10, pady=10, sticky=W)
        self.comment_entry = Entry(input_frame, width=30, font=("Arial", 11))
        self.comment_entry.grid(row=0, column=3, padx=10, pady=10)
        
        # Выбор категории 
        Label(input_frame, text="Категория:").grid(row=1, column=0, padx=10, pady=10, sticky=W)
        self.categories = ["Еда", "Транспорт", "Одежда", "Накопления", "Зарплата", "Прочее"]
        self.category_var = StringVar(value=self.categories[0])
        self.category_menu = ttk.Combobox(
            input_frame, 
            textvariable=self.category_var,
            values=self.categories,
            state="readonly",
            width=18
        )
        self.category_menu.grid(row=1, column=1, padx=10, pady=10)
        
        # Кнопки добавления
        self.income_btn = Button(
            input_frame, 
            text="➕ Добавить доход", 
            command=self.add_income,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 11, "bold"),
            width=18,
            height=1
        )
        self.income_btn.grid(row=1, column=2, padx=10, pady=10)
        
        self.expense_btn = Button(
            input_frame, 
            text="➖ Добавить расход", 
            command=self.add_expense,
            bg="#f44336",
            fg="white",
            font=("Arial", 11, "bold"),
            width=18,
            height=1
        )
        self.expense_btn.grid(row=1, column=3, padx=10, pady=10)
        
        # Панель с историей операций
        history_frame = LabelFrame(self.root, text="История операций", font=("Arial", 12, "bold"))
        history_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Таблица для отображения истории
        columns = ("Тип", "Категория", "Сумма", "Комментарий", "Дата")
        self.tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=15)
        
        # Настройка заголовков и ширины колонок
        self.tree.heading("Тип", text="Тип")
        self.tree.heading("Категория", text="Категория")
        self.tree.heading("Сумма", text="Сумма (₽)")
        self.tree.heading("Комментарий", text="Комментарий")
        self.tree.heading("Дата", text="Дата")
        
        self.tree.column("Тип", width=100)
        self.tree.column("Категория", width=120)
        self.tree.column("Сумма", width=100)
        self.tree.column("Комментарий", width=300)
        self.tree.column("Дата", width=150)
        
        # Скроллбар для таблицы
        scrollbar = ttk.Scrollbar(history_frame, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Размещение таблицы и скроллбара
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
    
    def add_transaction(self, trans_type, category, amount, comment):
        #Добавление транзакции в базу данных
        if amount <= 0:
            messagebox.showerror("Ошибка", "Сумма должна быть положительным числом!")
            return False
        
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.cursor.execute('''
            INSERT INTO transactions (type, category, amount, comment, date)
            VALUES (?, ?, ?, ?, ?)
        ''', (trans_type, category, amount, comment, date))
        self.conn.commit()
        
        return True
    
    def add_income(self):
        #Обработчик добавления дохода (FR5)
        try:
            amount = float(self.amount_entry.get())
            if amount <= 0:
                raise ValueError("Сумма должна быть положительной")
            
            comment = self.comment_entry.get().strip()
            category = self.category_var.get()
            
            # Добавление в базу данных
            if self.add_transaction("Доход", category, amount, comment):
                # Обновление баланса
                self.current_balance += amount
                self.update_balance_display()
                
                # Обновление таблицы
                self.load_transactions()
                
                # Очистка полей
                self.amount_entry.delete(0, END)
                self.comment_entry.delete(0, END)
                
                # Специальное сообщение 
                messagebox.showinfo("Успех", "Доход успешно добавлен!")
                
        except ValueError as e:
            # Обработка невалидных данных
            (NFR2)
            messagebox.showerror("Ошибка", f"Пожалуйста, введите корректную сумму!\n{str(e)}")
    
    def add_expense(self):
        #Обработчик добавления расхода
        try:
            amount = float(self.amount_entry.get())
            if amount <= 0:
                raise ValueError("Сумма должна быть положительной")
            
            comment = self.comment_entry.get().strip()
            category = self.category_var.get()
            
            # Добавление в базу данных
            if self.add_transaction("Расход", category, amount, comment):
                # Обновление баланса
                self.current_balance -= amount
                self.update_balance_display()
                
                # Обновление таблицы
                self.load_transactions()
                
                # Очистка полей
                self.amount_entry.delete(0, END)
                self.comment_entry.delete(0, END)
                
                messagebox.showinfo("Успех", "Расход успешно добавлен!")
                
        except ValueError as e:
            # Обработка невалидных данных
            messagebox.showerror("Ошибка", f"Пожалуйста, введите корректную сумму!\n{str(e)}")
    
    def load_transactions(self):
        #Загрузка и отображение истории операций из БД 
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Загрузка данных из базы
        self.cursor.execute('''
            SELECT type, category, amount, comment, date 
            FROM transactions 
            ORDER BY id DESC
        ''')
        
        for row in self.cursor.fetchall():
            trans_type, category, amount, comment, date = row
            # Форматирование суммы
            formatted_amount = f"{amount:.2f}"
            self.tree.insert("", END, values=(trans_type, category, formatted_amount, comment, date))
    
    def __del__(self):
        #Закрытие соединения с БД при завершении
        if hasattr(self, 'conn'):
            self.conn.close()

if __name__ == "__main__":
    root = Tk()
    app = BudgetApp(root)
    
    # Центрирование окна
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()
