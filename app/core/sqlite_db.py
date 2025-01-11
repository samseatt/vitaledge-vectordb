"""
File: sqlite_db.py
Module: app.core

Description:
------------
This module provides the `SQLiteDB` class, which serves as a lightweight, relational database interface 
for managing metadata and associated tags in a vector database system. It uses SQLite as the backend 
database engine, offering persistent storage and relational capabilities for metadata management.

The `SQLiteDB` class is designed to complement vector embeddings stored in a FAISS index. 
It stores textual metadata, external IDs, categories, and tags, allowing for robust administrative 
and search functionalities. By decoupling metadata storage from the FAISS vector IDs, this implementation 
ensures simplicity and flexibility when managing the relationship between embeddings and their associated data.

Responsibilities:
-----------------
- Manage SQLite database schema:
  - Create required tables (`vectors`, `tags`, and `vector_tags`) if they don't already exist.
  - Enable foreign key constraints to maintain relational integrity.
- Perform CRUD operations for metadata:
  - Add new metadata entries or update existing ones based on external IDs.
  - Retrieve metadata by vector ID, category, or tags.
  - Delete metadata entries and their associated tags.
- Provide an abstraction layer for metadata operations in higher-level services.

Dependencies:
-------------
- `sqlite3`: For managing the SQLite database connection and operations.
- `logging`: For logging actions and errors during database interactions.
- `typing`: For type annotations (`Optional`, `List`).

Usage:
------
The `SQLiteDB` class is typically used by higher-level services, such as `VectorDBService`, 
to perform metadata management and maintain relational consistency with FAISS.

Classes:
--------
- `SQLiteDB`: Encapsulates database operations for metadata management.

Methods:
--------
- `add_vector`: Add or update metadata associated with a vector.
- `get_vectors`: Retrieve metadata entries based on category or other filters.
- `get_text_by_id`: Fetch the textual metadata for a specific vector ID.
- `get_tags`: Retrieve all unique tags stored in the database.
- `delete_vector_by_vector_id`: Remove metadata and associated tags for a given vector ID.
- `get_all_metadata`: Fetch all metadata entries from the database.

Example:
--------
db = SQLiteDB(db_path="./data/sqlite_db.sqlite3")

# Adding a vector with metadata
vector_id = db.add_vector(
    text="Genomics study on rare diseases",
    external_id="study_001",
    category="genomics",
    tags=["genetics", "rare diseases"]
)

# Retrieving vectors by category
vectors = db.get_vectors(category="genomics")

# Deleting a vector by ID
db.delete_vector_by_vector_id(vector_id)

Design Considerations:
----------------------
- **Decoupling Metadata from FAISS IDs**:
  - Metadata is stored independently from FAISS embeddings, ensuring flexibility in operations 
    and avoiding potential ID conflicts.
  - Bridging between FAISS and SQLite is achieved via `text` metadata and embedding validations.
- **Tagging System**:
  - Tags are managed in a separate table (`tags`) and associated with vectors through a mapping table (`vector_tags`).
  - This design supports many-to-many relationships between vectors and tags.

Author:
-------
Sam Seatt

Date:
-----
2025-01-10

"""
import sqlite3
import logging
from typing import Optional, List

logger = logging.getLogger(__name__)

class SQLiteDB:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._initialize()

    def _initialize(self):
        """
        Initialize the SQLite database schema.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS vectors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                embed_id INTEGER UNIQUE,
                external_id TEXT,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tag TEXT UNIQUE
            );
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS vector_tags (
                vector_id INTEGER,
                tag_id INTEGER,
                PRIMARY KEY (vector_id, tag_id),
                FOREIGN KEY (vector_id) REFERENCES vectors (id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
            );
            """)
            conn.commit()

    def add_vector(self, text: str, embed_id: int, external_id: Optional[str], category: Optional[str], tags: List[str]) -> int:
    # def add_vector(self, text: str, external_id: Optional[str], category: Optional[str], tags: List[str]) ->int:
        """
        Add a vector and its associated tags to SQLite.

        Args:
            text (str): The text metadata associated with the vector.
            embed_id (int): The ID assigned to this embedding in Faiss.
            external_id (Optional[str]): An optional external identifier for the vector.
            category (Optional[str]): An optional category for the vector.
            tags (List[str]): A list of tags to associate with the vector.

        Returns:
            int: The ID of the inserted or updated vector.
        """
        logger.info(f"Called add_vector with embed_id: {embed_id}")
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Insert vector
            cursor.execute("""
            INSERT INTO vectors (text, embed_id, external_id, category)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(embed_id) DO UPDATE SET text=excluded.text, external_id=excluded.external_id, updated_at=CURRENT_TIMESTAMP
            """, (text, embed_id, external_id, category))
            # vector_id = cursor.lastrowid
            # Fetch the vector ID (safe for both insert and update cases)
            vector_id = cursor.lastrowid if cursor.lastrowid else cursor.execute(
                "SELECT id FROM vectors WHERE embed_id = ?;", (embed_id,)
            ).fetchone()[0]

            # Insert tags and their associations
            for tag in tags:
                cursor.execute("INSERT OR IGNORE INTO tags (tag) VALUES (?);", (tag,))
                tag_id = cursor.execute("SELECT id FROM tags WHERE tag = ?;", (tag,)).fetchone()[0]
                cursor.execute("INSERT OR IGNORE INTO vector_tags (vector_id, tag_id) VALUES (?, ?);", (vector_id, tag_id))

            conn.commit()
            return vector_id

    def get_vectors(self, category: Optional[str] = None) -> List[dict]:
        """
        Retrieve vectors based on category.

        Args:
            category (Optional[str]): The category to filter vectors.

        Returns:
            List[dict]: A list of vectors and their metadata.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if category:
                cursor.execute("SELECT * FROM vectors WHERE category = ?;", (category,))
            else:
                cursor.execute("SELECT * FROM vectors;")
            rows = cursor.fetchall()
        return [{"id": row[0], "text": row[1], "external_id": row[2], "category": row[3]} for row in rows]

    def get_text_by_id(self, vector_id: int) -> Optional[str]:
        """
        Retrieve the text for a given vector ID.

        Args:
            vector_id (int): The SQLite vector ID.

        Returns:
            Optional[str]: The associated text, or None if not found.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT text FROM vectors WHERE id = ?;", (vector_id,))
            result = cursor.fetchone()
        return result[0] if result else None

    def get_tags(self) -> List[dict]:
        """
        Retrieve all tags in SQLite.

        Returns:
            List[dict]: A list of tags.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tags;")
            rows = cursor.fetchall()
        return [{"id": row[0], "tag": row[1]} for row in rows]

    def get_metadata(self, vector_id: int) -> dict:
        """
        Retrieve metadata for a given vector ID.

        Args:
            vector_id (int): The ID of the vector.

        Returns:
            dict: Metadata including text, external_id, and tags.
        """
        logger.info(f"Called get_metadata with vector_id: {vector_id}")
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            logger.debug(f"Connected to sqlite with cursor: {cursor}")
            # Fetch text, external_id, and category from the vectors table
            cursor.execute("""
            SELECT id, text, external_id, category FROM vectors WHERE embed_id = ?;
            """, (int(vector_id),))
            row = cursor.fetchone()

            if not row:
                logger.info(f"No rows were fetched")
                return None

            logger.info(f"Rows fetched successfully")
            id, text, external_id, category = row
            logger.debug(f"Successfully retrieved vectors metadata for: {text}")

            # Fetch tags associated with the vector
            cursor.execute("""
            SELECT t.tag FROM tags t
            JOIN vector_tags vt ON vt.tag_id = t.id
            WHERE vt.vector_id = ?;
            """, (id,))
            tags = [tag[0] for tag in cursor.fetchall()]

            logger.info(f"Metadata received for text: {text}")
            return {
                "text": text,
                "external_id": external_id,
                "tags": tags,
                "category": category  # Optional if useful
            }

    def get_all_metadata(self):
        """
        Retrieve all metadata entries from the SQLite vectors table.

        Returns:
            List[dict]: All metadata entries.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Assuming metadata is stored in the `metadata` column of the `vectors` table
                cursor.execute("SELECT id, text, external_id, category, created_at, updated_at FROM vectors;")
                rows = cursor.fetchall()
                return [{"id": row[0], "text": row[1], "external_id": row[2], "category": row[3], "created_at": row[4], "updated_at": row[5]} for row in rows]
        except Exception as e:
            logger.error(f"Error while retrieving all metadata from SQLite: {e}")
            raise