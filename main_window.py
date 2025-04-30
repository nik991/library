from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableView, QLineEdit, QLabel, QMessageBox,
    QFormLayout, QSpinBox, QDateEdit, QComboBox
)
from PyQt6.QtCore import Qt, QAbstractTableModel
from PyQt6.QtGui import QAction
import sqlite3

class BooksTableModel(QAbstractTableModel):
    def __init__(self, data, headers):
        super().__init__()
        self._data = data
        self._headers = headers
    
    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            return str(self._data[index.row()][index.column()])
    
    def rowCount(self, index):
        return len(self._data)
    
    def columnCount(self, index):
        return len(self._headers)
    
    def headerData(self, section, orientation, role):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self._headers[section]
        return super().headerData(section, orientation, role)

class MainWindow(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setWindowTitle("Библиотека")
        self.setGeometry(100, 100, 800, 600)
        
        self.init_ui()
        self.load_books()
    
    def init_ui(self):
        # Создание меню
        menubar = self.menuBar()
        file_menu = menubar.addMenu("Файл")
        
        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Создание вкладок
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Вкладка "Книги"
        self.books_tab = QWidget()
        self.init_books_tab()
        self.tabs.addTab(self.books_tab, "Книги")
        
        # Вкладка "Читатели"
        self.readers_tab = QWidget()
        self.init_readers_tab()
        self.tabs.addTab(self.readers_tab, "Читатели")
        
        # Вкладка "Выдача книг"
        self.loans_tab = QWidget()
        self.init_loans_tab()
        self.tabs.addTab(self.loans_tab, "Выдача книг")
    
    def init_books_tab(self):
        layout = QVBoxLayout()
        
        # Поиск
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по названию или автору...")
        search_button = QPushButton("Поиск")
        search_button.clicked.connect(self.search_books)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        layout.addLayout(search_layout)
        
        # Таблица книг
        self.books_table = QTableView()
        layout.addWidget(self.books_table)
        
        # Кнопки управления
        buttons_layout = QHBoxLayout()
        add_button = QPushButton("Добавить книгу")
        add_button.clicked.connect(self.show_add_book_dialog)
        edit_button = QPushButton("Редактировать")
        edit_button.clicked.connect(self.show_edit_book_dialog)
        delete_button = QPushButton("Удалить")
        delete_button.clicked.connect(self.delete_book)
        buttons_layout.addWidget(add_button)
        buttons_layout.addWidget(edit_button)
        buttons_layout.addWidget(delete_button)
        layout.addLayout(buttons_layout)
        
        self.books_tab.setLayout(layout)
    
    def load_books(self):
        books = self.db.get_all_books()
        if books:
            headers = ["ID", "Название", "Автор", "Год", "Жанр", "ISBN", "Количество", "Доступно"]
            data = []
            for book in books:
                data.append([
                    book['id'],
                    book['title'],
                    book['author'],
                    book['year'],
                    book['genre'],
                    book['isbn'],
                    book['quantity'],
                    book['available']
                ])
            
            model = BooksTableModel(data, headers)
            self.books_table.setModel(model)
            self.books_table.resizeColumnsToContents()
    
    def search_books(self):
        search_term = self.search_input.text()
        if search_term:
            books = self.db.search_books(search_term)
            if books:
                headers = ["ID", "Название", "Автор", "Год", "Жанр", "ISBN", "Количество", "Доступно"]
                data = []
                for book in books:
                    data.append([
                        book['id'],
                        book['title'],
                        book['author'],
                        book['year'],
                        book['genre'],
                        book['isbn'],
                        book['quantity'],
                        book['available']
                    ])
                
                model = BooksTableModel(data, headers)
                self.books_table.setModel(model)
                self.books_table.resizeColumnsToContents()
            else:
                QMessageBox.information(self, "Поиск", "Книги не найдены")
    
    def show_add_book_dialog(self):
        dialog = AddBookDialog(self)
        if dialog.exec():
            book_data = dialog.get_book_data()
            if book_data:
                self.db.add_book(book_data)
                self.load_books()
                QMessageBox.information(self, "Успех", "Книга успешно добавлена")
    
    def show_edit_book_dialog(self):
        selected = self.books_table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите книгу для редактирования")
            return
        
        row = selected[0].row()
        book_id = self.books_table.model().index(row, 0).data()
        
        # Получаем данные книги из базы
        self.db.cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
        book = self.db.cursor.fetchone()
        
        if book:
            columns = [column[0] for column in self.db.cursor.description]
            book_data = dict(zip(columns, book))
            dialog = EditBookDialog(self, book_data)
            if dialog.exec():
                updated_data = dialog.get_book_data()
                if updated_data:
                    self.db.update_book(book_id, updated_data)
                    self.load_books()
                    QMessageBox.information(self, "Успех", "Книга успешно обновлена")
    
    def delete_book(self):
        selected = self.books_table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите книгу для удаления")
            return
        
        row = selected[0].row()
        book_id = self.books_table.model().index(row, 0).data()
        
        reply = QMessageBox.question(
            self, "Подтверждение",
            "Вы уверены, что хотите удалить эту книгу?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.db.delete_book(book_id):
                self.load_books()
                QMessageBox.information(self, "Успех", "Книга успешно удалена")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось удалить книгу")
    
    def init_readers_tab(self):
        # Аналогично init_books_tab, но для читателей
        pass
    
    def init_loans_tab(self):
        # Аналогично init_books_tab, но для выдачи книг
        pass

class AddBookDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить книгу")
        self.setModal(True)
        
        layout = QFormLayout()
        
        self.title_input = QLineEdit()
        self.author_input = QLineEdit()
        self.year_input = QSpinBox()
        self.year_input.setRange(0, 2100)
        self.year_input.setValue(2023)
        self.genre_input = QLineEdit()
        self.isbn_input = QLineEdit()
        self.quantity_input = QSpinBox()
        self.quantity_input.setRange(1, 1000)
        self.quantity_input.setValue(1)
        
        layout.addRow("Название:", self.title_input)
        layout.addRow("Автор:", self.author_input)
        layout.addRow("Год издания:", self.year_input)
        layout.addRow("Жанр:", self.genre_input)
        layout.addRow("ISBN:", self.isbn_input)
        layout.addRow("Количество:", self.quantity_input)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        layout.addRow(buttons)
        self.setLayout(layout)
    
    def get_book_data(self):
        return {
            'title': self.title_input.text(),
            'author': self.author_input.text(),
            'year': self.year_input.value(),
            'genre': self.genre_input.text(),
            'isbn': self.isbn_input.text(),
            'quantity': self.quantity_input.value(),
            'available': self.quantity_input.value()
        }

class EditBookDialog(AddBookDialog):
    def __init__(self, parent=None, book_data=None):
        super().__init__(parent)
        self.setWindowTitle("Редактировать книгу")
        
        if book_data:
            self.title_input.setText(book_data['title'])
            self.author_input.setText(book_data['author'])
            self.year_input.setValue(book_data['year'])
            self.genre_input.setText(book_data['genre'])
            self.isbn_input.setText(book_data['isbn'])
            self.quantity_input.setValue(book_data['quantity'])
