import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# Database setup
conn = sqlite3.connect("library.db", check_same_thread=False)
cursor = conn.cursor()

# Check if the table exists and has the correct columns
cursor.execute("PRAGMA table_info(books)")
columns = [col[1] for col in cursor.fetchall()]

if "rating" not in columns:
    cursor.execute("ALTER TABLE books ADD COLUMN rating INTEGER DEFAULT 3")
if "notes" not in columns:
    cursor.execute("ALTER TABLE books ADD COLUMN notes TEXT DEFAULT ''")
conn.commit()

# Add Book Function
def add_book(title, author, genre, status, rating, notes):
    cursor.execute("INSERT INTO books (title, author, genre, status, rating, notes) VALUES (?, ?, ?, ?, ?, ?)",
                   (title, author, genre, status, rating, notes))
    conn.commit()

# View Books Function
def get_books():
    return pd.read_sql("SELECT * FROM books", conn)

# Delete Book Function
def delete_book(book_id):
    cursor.execute("DELETE FROM books WHERE id=?", (book_id,))
    conn.commit()

# Update Rating & Notes
def update_book(book_id, rating, notes):
    cursor.execute("UPDATE books SET rating=?, notes=? WHERE id=?", (rating, notes, book_id))
    conn.commit()

# Streamlit UI
st.title("📚 Personal Library Manager")

menu = ["Add Book", "View Library", "Analytics", "Update Book"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Add Book":
    st.subheader("Add a New Book")
    title = st.text_input("Title")
    author = st.text_input("Author")
    genre = st.selectbox("Genre", ["Fiction", "Non-Fiction", "Science", "Fantasy", "Other"])
    status = st.selectbox("Status", ["Read", "Unread"])
    rating = st.slider("Rating (1-5)", 1, 5, 3)
    notes = st.text_area("Personal Notes")
    
    if st.button("Add Book"):
        add_book(title, author, genre, status, rating, notes)
        st.success(f"Added '{title}' to the library!")

elif choice == "View Library":
    st.subheader("Your Book Collection")
    df = get_books()
    st.dataframe(df)

    if not df.empty:
        delete_id = st.number_input("Enter Book ID to Delete", min_value=1, step=1)
        if st.button("Delete Book"):
            delete_book(delete_id)
            st.warning("Book Deleted. Refresh to see changes.")

elif choice == "Analytics":
    st.subheader("📊 Library Insights")
    df = get_books()
    
    if not df.empty:
        genre_count = df['genre'].value_counts()
        st.bar_chart(genre_count)
        
        status_count = df['status'].value_counts()
        fig, ax = plt.subplots()
        ax.pie(status_count, labels=status_count.index, autopct='%1.1f%%', startangle=90, colors=["#ff9999", "#66b3ff"])
        ax.axis('equal')
        st.pyplot(fig)

elif choice == "Update Book":
    st.subheader("Update Book Rating & Notes")
    df = get_books()
    if not df.empty:
        book_id = st.number_input("Enter Book ID to Update", min_value=1, step=1)
        rating = st.slider("New Rating (1-5)", 1, 5, 3)
        notes = st.text_area("New Notes")
        
        if st.button("Update Book"):
            update_book(book_id, rating, notes)
            st.success("Book updated successfully! Refresh to see changes.")

