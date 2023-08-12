import os
from app import create_app, db
from flask_migrate import Migrate
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
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

