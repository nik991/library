import sys
from PyQt6.QtWidgets import QApplication
from library_database import LibraryDatabase
from main_window import MainWindow

def main():
    # Инициализация базы данных
    db = LibraryDatabase()
    db.initialize_database()
    
    # Создание приложения
    app = QApplication(sys.argv)
    
    # Создание главного окна
    window = MainWindow(db)
    window.show()
    
    # Запуск приложения
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
