import sqlite3
from typing import List, Dict, Optional

class LibraryDatabase:
    def __init__(self, db_name: str = "library.db"):
        self.db_name = db_name
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
    
    def initialize_database(self):
        """Создание таблиц базы данных, если они не существуют"""
        # Таблица книг
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            year INTEGER,
            genre TEXT,
            isbn TEXT,
            quantity INTEGER DEFAULT 1,
            available INTEGER DEFAULT 1
        )
        """)
        
        # Таблица читателей
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS readers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            address TEXT
        )
        """)
        
        # Таблица выдачи книг
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS book_loans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            reader_id INTEGER NOT NULL,
            loan_date TEXT NOT NULL,
            return_date TEXT,
            FOREIGN KEY (book_id) REFERENCES books (id),
            FOREIGN KEY (reader_id) REFERENCES readers (id)
        )
        """)
        
        self.connection.commit()
    
    def add_book(self, book_data: Dict) -> int:
        """Добавление новой книги в базу данных"""
        query = """
        INSERT INTO books (title, author, year, genre, isbn, quantity, available)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        self.cursor.execute(query, (
            book_data['title'],
            book_data['author'],
            book_data['year'],
            book_data['genre'],
            book_data['isbn'],
            book_data['quantity'],
            book_data['available']
        ))
        self.connection.commit()
        return self.cursor.lastrowid
    
    def get_all_books(self) -> List[Dict]:
        """Получение списка всех книг"""
        self.cursor.execute("SELECT * FROM books")
        columns = [column[0] for column in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
    
    def search_books(self, search_term: str) -> List[Dict]:
        """Поиск книг по названию или автору"""
        query = """
        SELECT * FROM books 
        WHERE title LIKE ? OR author LIKE ?
        """
        self.cursor.execute(query, (f"%{search_term}%", f"%{search_term}%"))
        columns = [column[0] for column in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
    
    def update_book(self, book_id: int, book_data: Dict) -> bool:
        """Обновление информации о книге"""
        query = """
        UPDATE books 
        SET title = ?, author = ?, year = ?, genre = ?, isbn = ?, quantity = ?, available = ?
        WHERE id = ?
        """
        self.cursor.execute(query, (
            book_data['title'],
            book_data['author'],
            book_data['year'],
            book_data['genre'],
            book_data['isbn'],
            book_data['quantity'],
            book_data['available'],
            book_id
        ))
        self.connection.commit()
        return self.cursor.rowcount > 0
    
    def delete_book(self, book_id: int) -> bool:
        """Удаление книги из базы данных"""
        self.cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
        self.connection.commit()
        return self.cursor.rowcount > 0
    
    def close(self):
        """Закрытие соединения с базой данных"""
        self.connection.close()
