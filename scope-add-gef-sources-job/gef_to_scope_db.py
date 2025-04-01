#!/usr/bin/env python3
"""
Script to migrate GEF documents from SQLite to the Scope MySQL database source table.
Ensures no duplicates are created and only creates the source type once.
"""
import argparse
import logging
import sqlalchemy
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    Integer,
    String,
    Text,
    DateTime,
    select,
)
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Constants
GEF_SOURCE_TYPE_NAME = "GEF Document"
GEF_SOURCE_TYPE_DESC = "Documents from the Global Environment Facility portal"


def get_args():
    parser = argparse.ArgumentParser(
        description="Migrate GEF documents to Scope database"
    )
    parser.add_argument(
        "--gef-db-path", required=True, help="Path to the GEF document SQLite database"
    )
    parser.add_argument("--mysql-host", required=True, help="MySQL host")
    parser.add_argument(
        "--mysql-db", default="scopesql", help="MySQL database name (default: scopesql)"
    )
    parser.add_argument("--mysql-user", required=True, help="MySQL username")
    parser.add_argument("--mysql-password", required=True, help="MySQL password")
    parser.add_argument(
        "--batch-size", type=int, default=100, help="Batch size for processing"
    )
    parser.add_argument("--dry-run", action="store_true", help="Perform a dry run")
    return parser.parse_args()


def get_engines(args):
    """Create SQLAlchemy engines for both databases"""
    sqlite_url = f"sqlite:///{args.gef_db_path}"
    mysql_url = f"mysql+mysqlconnector://{args.mysql_user}:{args.mysql_password}@{args.mysql_host}/{args.mysql_db}"

    # Read-only engine for SQLite
    sqlite_engine = create_engine(sqlite_url, connect_args={"mode": "ro"})
    mysql_engine = create_engine(mysql_url)

    return sqlite_engine, mysql_engine


def define_tables():
    """Define tables based on the actual database structure"""
    # SQLite document table
    sqlite_metadata = MetaData()
    document_table = Table(
        "document",
        sqlite_metadata,
        Column("id", Integer, primary_key=True),
        Column("original_filename", String),
        Column("download_url", String, index=True),
        Column("document_type", String),
        Column("project_id", String),
        Column("last_updated", DateTime, default=datetime.utcnow),
    )

    # MySQL tables (scopeBackend_sourcetype and scopeBackend_source)
    mysql_metadata = MetaData()
    source_type_table = Table(
        "scopeBackend_sourcetype",
        mysql_metadata,
        Column("id", Integer, primary_key=True),
        Column("name", String(255)),
        Column("description", Text),
    )

    source_table = Table(
        "scopeBackend_source",
        mysql_metadata,  # Note the correct table name here
        Column("id", Integer, primary_key=True),
        Column("text", Text),
        Column("url", String(255)),
        Column("sourceType_id", Integer),
    )

    return document_table, source_type_table, source_table


def get_or_create_source_type(mysql_engine, source_type_table, dry_run=False):
    """Get or create GEF source type in MySQL database"""
    try:
        with mysql_engine.connect() as conn:
            # Check if source type exists
            query = select(source_type_table.c.id).where(
                source_type_table.c.name == GEF_SOURCE_TYPE_NAME
            )
            result = conn.execute(query).fetchone()

            if result:
                logger.info(
                    f"Found existing source type: {GEF_SOURCE_TYPE_NAME} (ID: {result[0]})"
                )
                return result[0]

            # Create new source type
            if dry_run:
                logger.info(
                    f"[DRY RUN] Would create source type: {GEF_SOURCE_TYPE_NAME}"
                )
                return -1

            insert = source_type_table.insert().values(
                name=GEF_SOURCE_TYPE_NAME, description=GEF_SOURCE_TYPE_DESC
            )
            result = conn.execute(insert)
            conn.commit()

            source_type_id = result.inserted_primary_key[0]
            logger.info(
                f"Created new source type: {GEF_SOURCE_TYPE_NAME} (ID: {source_type_id})"
            )
            return source_type_id
    except SQLAlchemyError as e:
        logger.error(f"Error getting/creating source type: {e}")
        raise


def get_existing_sources(mysql_engine, source_table):
    """Get a set of existing source texts to check for duplicates efficiently"""
    try:
        with mysql_engine.connect() as conn:
            query = select(source_table.c.text, source_table.c.url)
            rows = conn.execute(query).fetchall()
            # Create a set of (text, url) tuples for efficient lookup
            return {(row.text, row.url) for row in rows}
    except SQLAlchemyError as e:
        logger.error(f"Error getting existing sources: {e}")
        return set()


def migrate_documents(
    sqlite_engine,
    mysql_engine,
    document_table,
    source_table,
    source_type_id,
    batch_size,
    dry_run=False,
):
    """Migrate documents from SQLite to MySQL"""
    # Get existing sources to prevent duplicates
    existing_sources = get_existing_sources(mysql_engine, source_table)
    logger.info(f"Found {len(existing_sources)} existing sources in MySQL database")

    try:
        # Get total document count
        with sqlite_engine.connect() as sqlite_conn:
            count_query = select(sqlalchemy.func.count()).select_from(document_table)
            total_count = sqlite_conn.execute(count_query).scalar()
            logger.info(f"Found {total_count} documents in GEF database")

            # Process in batches to avoid memory issues
            offset = 0
            inserted_count = 0
            skipped_count = 0

            while offset < total_count:
                query = select(document_table).limit(batch_size).offset(offset)
                documents = sqlite_conn.execute(query).fetchall()
                if not documents:
                    break

                to_insert = []
                for doc in documents:
                    # Skip documents with missing fields
                    if (
                        not doc.project_id
                        or not doc.original_filename
                        or not doc.download_url
                    ):
                        skipped_count += 1
                        continue

                    text = f"{doc.project_id}/{doc.original_filename}"
                    url = doc.download_url

                    # Check for duplicates
                    if (text, url) in existing_sources:
                        logger.debug(f"Source already exists: {text}")
                        skipped_count += 1
                        continue

                    # Add to batch
                    to_insert.append(
                        {"text": text, "url": url, "sourceType_id": source_type_id}
                    )
                    # Mark as existing to prevent duplicates in future batches
                    existing_sources.add((text, url))

                # Insert batch
                if to_insert and not dry_run:
                    with mysql_engine.connect() as mysql_conn:
                        mysql_conn.execute(source_table.insert(), to_insert)
                        mysql_conn.commit()

                inserted_count += len(to_insert)
                if dry_run:
                    logger.info(
                        f"[DRY RUN] Would insert {len(to_insert)} sources (processed {offset+len(documents)}/{total_count})"
                    )
                else:
                    logger.info(
                        f"Inserted {len(to_insert)} sources (processed {offset+len(documents)}/{total_count})"
                    )

                offset += batch_size

    except SQLAlchemyError as e:
        logger.error(f"Database error during migration: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during migration: {e}")
        raise

    return total_count, inserted_count, skipped_count


def main():
    args = get_args()

    try:
        # Connect to databases
        sqlite_engine, mysql_engine = get_engines(args)

        # Define table structures
        document_table, source_type_table, source_table = define_tables()

        # Get or create source type
        source_type_id = get_or_create_source_type(
            mysql_engine, source_type_table, args.dry_run
        )

        # Migrate documents
        total_docs, inserted_docs, skipped_docs = migrate_documents(
            sqlite_engine,
            mysql_engine,
            document_table,
            source_table,
            source_type_id,
            args.batch_size,
            args.dry_run,
        )

        logger.info(f"Migration summary:")
        logger.info(f"- Total documents: {total_docs}")
        logger.info(f"- Inserted: {inserted_docs}")
        logger.info(f"- Skipped: {skipped_docs}")

        if args.dry_run:
            logger.info(
                "This was a dry run. No changes were made to the MySQL database."
            )

    except Exception as e:
        logger.error(f"Error during migration: {e}")
        exit(1)


if __name__ == "__main__":
    main()
