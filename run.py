import os
import click
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

from app import create_app, db
from flask_migrate import Migrate, upgrade
from app.models import User, Phrase, WordList, Comment, Example

app = create_app(os.environ.get('FLASK_CONFIG') or 'default')
migrage = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Phrase=Phrase, WordList=WordList,
                Comment=Comment, Example=Example)

@app.cli.command()
def test():
    """Run the unit tests."""
    run_tests('tests')

@app.cli.command('functional-test')
@click.argument('name', required=False)
def functional_test(name=None):
    """Run the unit tests."""
    run_tests('functional_tests', name)

def run_tests(folder, name=None):
    import unittest
    if name:
        tests = unittest.TestLoader().discover(folder , pattern=name + '.py')
    else:
        tests = unittest.TestLoader().discover(folder)
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        exit(0)
    else:
        exit(1)

@app.cli.command()
def deploy():
    upgrade()
