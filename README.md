# CSGO Telnet

Little program to use the `-netconport` launch option in CS:GO for chat commands.

# How to use

Set launch option `-netconport PORT`. PORT can be any port you want as long as you change it in your program aswell. 

# Examples

All examples can be found in the `examples` folder.

* `full-example.py`: This is an example showing most of the functionality in one script.
* `jumpstats.py`: Small programs to save jumpstats to a file using `on_incoming_data()`.
* `moving-clantag.py`: This lets you have a changing clantag in game, so it looks like you're using a cheat.
* `name-from-steamid.py`: This showcases the `set_name_from_steamid()` function.

To run an example, copy it to the project's root directory and run it with python.

# Limitations

* Chat parsing only works if CS:GO is in the game's English (Custom languages won't work if you changed the way chat looks). If you set a different langauge, you'll have to change some things in `ChatMessage`
* Chat messages are delayed by 0.7s if the owner is the one executing the command. This makes sure CS:GO doesn't block the message because you're sending messages too fast.
* The program can only read/write to console. If something doesn't show up in console this utility can't react to it.

# Screenshots

These are all results from `examples/full-example.py`.

### Ping Command
![Ping Command](screenshots/ping-command.png)

### Time Command
![Time Command](screenshots/time-command.png)

### Terminal Output
![Terminal Output](screenshots/terminal-output.png)
