from app import create_app, db
from app.models.user import User
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def create_database():
    try:
        # Connect to PostgreSQL server
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            password='Ee27951352!',
            host='localhost'
        )

        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'vm_manager_test'")
        exists = cursor.fetchone()

        if not exists:
            cursor.execute('CREATE DATABASE vm_manager_test')
            print("Database created!")

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error creating database: {e}")


def init_db():
    try:
        # Create database if doesn't exist
        create_database()

        # Initialize Flask app and create tables
        app = create_app()
        with app.app_context():
            db.create_all()

            # Create admin user if doesn't exist
            if not User.query.filter_by(username='admin').first():
                admin = User(
                    username='admin',
                    email='admin@example.com'


                )
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                print("Admin user created!")

    except Exception as e:
        print(f"Error initializing database: {e}")


if __name__ == '__main__':
    init_db()
