one folder will be chatcli under which there will be:
chatcli(the folder that contains __init__.py and cli.py) and setup.py

in another place, run main_server.py

From your project root(where setup.py is) run this command in the windows command prompt:
pip install -e .

Now you can run:
1. chatcli start-server
2. chatcli join

For help:
1. chatci --help
