# Intel Python Course Telegram Bot

This is a repository for Telegram bot that will be developed during Intel Academic Program Python Course.

## Set up Python environment

1. Create virtual environment `python -m venv venv`
2. Activate virtual environment and install requirements: 

    `venv\Scripts\activate` - on Linux
    
    `venv\Scripts\activate.bat` - on Windows
    
    `pip install -r requirements.txt`

## Create your Telegram Bot

1. Follow official [Telegram instructions](https://core.telegram.org/bots) to create your bot and obtain token.
2. Insert obtained token to `setup.py` `TOKEN` variable.

## Run your bot

1. Execute ``python chat_bot_template.py``
2. Try your bot - find it in Telegram and press `/start`.

## Run unit tests
1. via unittests ``python -m unittest discover -v tests``
2. via pytest with html report: ``pytest -s tests --self-contained-html --html=tests.html --capture=sys``

## Run tests with coverage
Install a package ``pip install coverage``
Execute ``coverage run -m unittest discover tests && coverage report -m && coverage html``
See html report in <project_root>/htmlcov/index.html

## Run linter check
Install a package ``pip install flake8``
Execute ``flake8 <project_root> --config=setup.cfg --output-file=flake8_check.log``
