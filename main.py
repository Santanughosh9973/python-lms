import json
import os
import re
from datetime import date, datetime


DATA_DIR = "data"
BOOKS_FILE = os.path.join(DATA_DIR, "books.json")
STUDENTS_FILE = os.path.join(DATA_DIR, "students.json")
TRANSACTIONS_FILE = os.path.join(DATA_DIR, "transactions.json")

FINE_PER_DAY = 5


class Book:
    def __init__(self, book_id, title, author, quantity):
        self.id = book_id
        self.title = title
        self.author = author
        self.quantity = quantity

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "quantity": self.quantity
        }


class Student:
    def __init__(self, student_id, name, email):
        self.id = student_id
        self.name = name
        self.email = email

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email
        }


class Library:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)

        self.books = self.load_data(BOOKS_FILE)
        self.students = self.load_data(STUDENTS_FILE)
        self.transactions = self.load_data(TRANSACTIONS_FILE)

    @staticmethod
    def load_data(filename):
        if not os.path.exists(filename):
            with open(filename, "w", encoding="utf-8") as file:
                json.dump([], file, indent=4)
            return []

        try:
            with open(filename, "r", encoding="utf-8") as file:
                data = json.load(file)
                return data if isinstance(data, list) else []

        except (json.JSONDecodeError, OSError):
            print(
                f"Warning: Could not read {filename}. "
                "Starting with an empty list."
            )
            return []

    @staticmethod
    def save_data(filename, data):
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def save_all(self):
        self.save_data(BOOKS_FILE, self.books)
        self.save_data(STUDENTS_FILE, self.students)
        self.save_data(TRANSACTIONS_FILE, self.transactions)

    def find_book(self, book_id):
        return next(
            (
                book for book in self.books
                if book["id"].lower() == book_id.lower()
            ),
            None
        )

    def find_student(self, student_id):
        return next(
            (
                student for student in self.students
                if student["id"].lower() == student_id.lower()
            ),
            None
        )

    def available_copies(self, book_id):
        book = self.find_book(book_id)

        if book is None:
            return 0

        issued_count = sum(
            1 for transaction in self.transactions
            if transaction["book_id"] == book_id
            and transaction["status"] == "Issued"
        )

        return max(0, book["quantity"] - issued_count)

    # ADD BOOK
    def add_book(self):
        print("\n--- Add Book ---")

        title = input("Enter book title: ").strip()
        author = input("Enter author name: ").strip()

        if not title or not author:
            print("Title and author cannot be empty.")
            return

        # AUTHOR VALIDATION
        if not re.fullmatch(r"[A-Za-z ]+", author):
            print(
                "Invalid author name! "
                "Use letters and spaces only."
            )
            return

        try:
            quantity = int(input("Enter number of copies: "))

            if quantity < 1:
                raise ValueError

        except ValueError:
            print("Please enter a whole number greater than zero.")
            return

        for book in self.books:
            if (
                book["title"].lower() == title.lower()
                and book["author"].lower() == author.lower()
            ):
                book["quantity"] += quantity
                self.save_all()

                print(
                    f"Book already existed. Quantity increased "
                    f"to {book['quantity']}."
                )
                return

        book_id = "B" + datetime.now().strftime("%y%m%d%H%M%S")

        self.books.append(
            Book(book_id, title, author, quantity).to_dict()
        )

        self.save_all()

        print(f"Book added successfully. Book ID: {book_id}")

    # DISPLAY BOOKS
    def display_books(self, only_available=False):
        print("\n--- Book List ---")

        if not self.books:
            print("No books found.")
            return

        print(
            f"{'ID':<16} {'TITLE':<30} {'AUTHOR':<25} "
            f"{'TOTAL':<8} {'AVAILABLE':<10}"
        )
        print("-" * 95)

        for book in self.books:
            available = self.available_copies(book["id"])

            if only_available and available == 0:
                continue

            print(
                f"{book['id']:<16} "
                f"{book['title'][:29]:<30} "
                f"{book['author'][:24]:<25} "
                f"{book['quantity']:<8} "
                f"{available:<10}"
            )

    # SEARCH BOOKS
    def search_books(self):
        query = input(
            "Enter a book ID, title, or author to search: "
        ).strip().lower()

        matches = [
            book for book in self.books
            if query in book["id"].lower()
            or query in book["title"].lower()
            or query in book["author"].lower()
        ]

        if not matches:
            print("No matching books found.")
            return

        print("\nSearch results:")

        for book in matches:
            print(
                f"ID: {book['id']} | "
                f"Title: {book['title']} | "
                f"Author: {book['author']} | "
                f"Available: {self.available_copies(book['id'])}"
                f"/{book['quantity']}"
            )

    # REGISTER STUDENT
    def register_student(self):
        print("\n--- Register Student ---")

        name = input("Enter student name: ").strip()
        email = input("Enter student email: ").strip()

        if not name or not email or "@" not in email:
            print(
                "Please enter a name and a valid-looking email address."
            )
            return

        if any(
            student["email"].lower() == email.lower()
            for student in self.students
        ):
            print("A student with this email is already registered.")
            return

        student_id = "S" + datetime.now().strftime("%y%m%d%H%M%S")

        self.students.append(
            Student(student_id, name, email).to_dict()
        )

        self.save_all()

        print(
            f"Student registered successfully. Student ID: {student_id}"
        )

    # DISPLAY STUDENTS
    def display_students(self):
        print("\n--- Student List ---")

        if not self.students:
            print("No students registered.")
            return

        for student in self.students:
            print(
                f"ID: {student['id']} | "
                f"Name: {student['name']} | "
                f"Email: {student['email']}"
            )

    # ISSUE BOOK
    def issue_book(self):
        print("\n--- Issue Book ---")

        book_id = input("Enter book ID: ").strip()
        student_id = input("Enter student ID: ").strip()

        book = self.find_book(book_id)
        student = self.find_student(student_id)

        if book is None:
            print("Error: Invalid book ID.")
            return

        if student is None:
            print("Error: Invalid student ID. Register the student first.")
            return

        if self.available_copies(book["id"]) < 1:
            print("No copies of this book are currently available.")
            return

        due_text = input(
            "Enter due date (YYYY-MM-DD): "
        ).strip()

        try:
            due_date = date.fromisoformat(due_text)

            if due_date < date.today():
                print("Due date cannot be in the past.")
                return

        except ValueError:
            print(
                "Invalid date. Use YYYY-MM-DD, "
                "for example 2026-10-20."
            )
            return

        transaction_id = "T" + datetime.now().strftime("%y%m%d%H%M%S")

        self.transactions.append({
            "id": transaction_id,
            "book_id": book["id"],
            "book_title": book["title"],
            "student_id": student["id"],
            "student_name": student["name"],
            "issued_on": date.today().isoformat(),
            "due_date": due_date.isoformat(),
            "returned_on": None,
            "fine": 0,
            "status": "Issued"
        })

        self.save_all()

        print(
            f"Book '{book['title']}' issued to {student['name']}."
        )
        print(
            f"Transaction ID: {transaction_id} | "
            f"Due date: {due_date.isoformat()}"
        )

    # RETURN BOOK
    def return_book(self):
        print("\n--- Return Book ---")

        transaction_id = input(
            "Enter transaction ID: "
        ).strip()

        transaction = next(
            (
                item for item in self.transactions
                if item["id"].lower() == transaction_id.lower()
            ),
            None
        )

        if transaction is None:
            print("Error: Invalid transaction ID.")
            return

        if transaction["status"] != "Issued":
            print("This book has already been returned.")
            return

        returned_date = date.today()
        due_date = date.fromisoformat(transaction["due_date"])

        overdue_days = max(
            0, (returned_date - due_date).days
        )

        fine = overdue_days * FINE_PER_DAY

        transaction["returned_on"] = returned_date.isoformat()
        transaction["fine"] = fine
        transaction["status"] = "Returned"

        self.save_all()

        print(
            f"Book '{transaction['book_title']}' returned successfully."
        )
        print(f"Overdue days: {overdue_days}")
        print(f"Fine: Rs. {fine}")

    # DISPLAY TRANSACTIONS
    def display_transactions(self):
        print("\n--- Book Transactions ---")

        if not self.transactions:
            print("No transactions found.")
            return

        for item in sorted(
            self.transactions,
            key=lambda transaction: transaction["issued_on"],
            reverse=True
        ):
            print(
                f"Transaction: {item['id']} | "
                f"Book: {item['book_title']} | "
                f"Student: {item['student_name']} | "
                f"Issued: {item['issued_on']} | "
                f"Due: {item['due_date']} | "
                f"Status: {item['status']} | "
                f"Fine: Rs. {item['fine']}"
            )

    # STATISTICS
    def statistics(self):
        issued = [
            transaction for transaction in self.transactions
            if transaction["status"] == "Issued"
        ]

        available = sum(
            self.available_copies(book["id"])
            for book in self.books
        )

        total_copies = sum(
            book["quantity"] for book in self.books
        )

        issue_counts = {}

        for transaction in self.transactions:
            title = transaction["book_title"]
            issue_counts[title] = (
                issue_counts.get(title, 0) + 1
            )

        popular = sorted(
            issue_counts.items(),
            key=lambda item: item[1],
            reverse=True
        )

        print("\n--- Library Statistics ---")
        print(f"Different book titles: {len(self.books)}")
        print(f"Total book copies: {total_copies}")
        print(f"Available copies: {available}")
        print(f"Currently issued copies: {len(issued)}")
        print(f"Registered students: {len(self.students)}")
        print(
            f"Total issue transactions: {len(self.transactions)}"
        )

        print("\nMost issued books:")

        if not popular:
            print("No issue history yet.")
        else:
            for number, (title, count) in enumerate(
                popular[:5], start=1
            ):
                print(
                    f"{number}. {title} — {count} issue(s)"
                )


def main():
    library = Library()

    while True:
        print("\n========== LIBRARY MANAGEMENT SYSTEM ==========")
        print("1. Add a book")
        print("2. Display all books")
        print("3. Display available books")
        print("4. Search books")
        print("5. Register a student")
        print("6. Display students")
        print("7. Issue a book")
        print("8. Return a book")
        print("9. Display transactions")
        print("10. Show statistics")
        print("0. Exit")

        choice = input("Enter your choice: ").strip()

        actions = {
            "1": library.add_book,
            "2": library.display_books,
            "3": lambda: library.display_books(only_available=True),
            "4": library.search_books,
            "5": library.register_student,
            "6": library.display_students,
            "7": library.issue_book,
            "8": library.return_book,
            "9": library.display_transactions,
            "10": library.statistics
        }

        if choice == "0":
            library.save_all()
            print("Records saved. Goodbye!")
            break

        action = actions.get(choice)

        if action:
            try:
                action()
            except (KeyError, TypeError, OSError) as error:
                print(
                    f"An operation could not be completed: {error}"
                )
        else:
            print(
                "Invalid choice. Please select a number from 0 to 10."
            )


if __name__ == "__main__":
    main()
