# cli.py
import click
from app import app, db # Import necessary objects from the main app

# Create a custom command group for database tasks
# This will be available as 'flask db'
@app.cli.group()
def db_commands():
    """Database administration commands."""
    pass

@db_commands.command('create')
def create_db():
    """Creates all database tables based on the models defined in app.py."""
    
    with app.app_context():
        try:
            db.create_all()
            click.echo("✅ Database tables created successfully.")
        except Exception as e:
            click.echo(f"❌ ERROR: Failed to create database tables. Error: {e}")