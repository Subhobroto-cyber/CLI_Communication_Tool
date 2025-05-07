one folder will chatcli under which there will be:
chatcli(the folder that contains init.py and cli.py) and setup.py

in another place run main_server.py

From your project root(where setup.py is) run this command in the windows command prompt:
pip install -e .

Now you can run:
chatcli start-server
chatcli join

For help:
chatci --help
