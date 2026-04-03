"""
Script chèn 1 triệu bản ghi vào bảng books
Chạy: python seed_data.py
"""
import pymysql
import random
import time

DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'cuong912005',
    'database': 'book_management',
    'charset': 'utf8mb4'
}

# Sample data for random generation
TITLES = [
    "The Art of", "Introduction to", "Advanced", "Modern", "Complete Guide to",
    "Mastering", "Learning", "Professional", "Essential", "Practical",
    "Fundamentals of", "Beginning", "Expert", "Ultimate", "Effective"
]

SUBJECTS = [
    "Programming", "Python", "Java", "JavaScript", "Database Design",
    "Machine Learning", "Web Development", "Data Science", "Algorithms",
    "Software Engineering", "Cloud Computing", "Cybersecurity", "DevOps",
    "Artificial Intelligence", "Mobile Development", "React", "Node.js",
    "System Design", "Computer Networks", "Operating Systems"
]

AUTHORS_FIRST = [
    "John", "Jane", "Michael", "Sarah", "David", "Emily", "Robert", "Lisa",
    "William", "Jennifer", "James", "Maria", "Richard", "Susan", "Thomas",
    "Linda", "Charles", "Barbara", "Daniel", "Elizabeth"
]

AUTHORS_LAST = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"
]

GENRES = [
    "Programming", "Technology", "Science", "Education", "Reference",
    "Computer Science", "Software", "Engineering", "Mathematics", "Business"
]


def generate_book(index):
    title = f"{random.choice(TITLES)} {random.choice(SUBJECTS)} {index}"
    author = f"{random.choice(AUTHORS_FIRST)} {random.choice(AUTHORS_LAST)}"
    published_year = random.randint(1990, 2024)
    genre = random.choice(GENRES)
    price = round(random.uniform(9.99, 99.99), 2)
    return (title, author, published_year, genre, price)


def insert_books(total=1000000, batch_size=10000):
    """Insert books in batches for better performance"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    print(f"🚀 Starting to insert {total:,} records...")
    print(f"📦 Batch size: {batch_size:,}")
    
    start_time = time.time()
    inserted = 0
    
    sql = """
        INSERT INTO books (title, author, published_year, genre, price)
        VALUES (%s, %s, %s, %s, %s)
    """
    
    while inserted < total:
        batch = []
        batch_count = min(batch_size, total - inserted)
        
        for i in range(batch_count):
            batch.append(generate_book(inserted + i + 1))
        
        cursor.executemany(sql, batch)
        conn.commit()
        
        inserted += batch_count
        elapsed = time.time() - start_time
        rate = inserted / elapsed if elapsed > 0 else 0
        
        print(f"✅ Inserted: {inserted:,} / {total:,} ({inserted*100//total}%) - {rate:.0f} records/sec")
    
    cursor.close()
    conn.close()
    
    total_time = time.time() - start_time
    print(f"\n🎉 Done! Inserted {total:,} records in {total_time:.2f} seconds")
    print(f"📊 Average speed: {total/total_time:.0f} records/second")


if __name__ == '__main__':
    insert_books(total=1000000, batch_size=10000)
