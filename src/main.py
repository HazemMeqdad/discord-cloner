from time import sleep
from colner import Guild, Restart, Copy


words = "\x1b[6;30;42m[ This tool made by: H A Z E M#1629 ]\x1b[0m\nhttps://github.com/HazemMeqdad\nSupport: https://discord.gg/VcWRRphVQB\n"
for char in words:
    sleep(0.1)
    print(char, end='', flush=True)

token = input("Insert token here: ")

commands = {
    "restart": {
        ".restart",
    },
    "copy": {
        ".copy -all",
        ".copy -roles",
        ".copy -emojis",
        ".copy -settings"
    },
    "exit": {
        ".exit"
    }
}


def main():
    stats = True  # to not error if use exit() method
    print("====================================================")
    while stats:

        command = input("Enter command more info \033[91m.help\033[0m >>> ")

        if command.startswith(".exit"):  # to exit from tool

            stats = False  # to not get error from stop wihle loop
            exit(-1)

        # to get all commands and author creator
        elif command.startswith(".help"):

            print("Copyright: https://github.com/HazemMeqdad\nSupport: https://discord.gg/VcWRRphVQB")
            z = ""
            for com, d in commands.items():  # make help command
                z += com + "\n"
                for i in d:
                    z += "  " + i + "\n"
            print(z)

        # to restart all objects from guild example: roles, channels, emojis, ...
        elif command.startswith(".restart"):

            guild_id = input("Give me server id: ")
            guild = Guild(guild_id, token)

            if guild.get_info.get("code"):
                print("\033[91mInvalid server id\033[0m")
                continue
            print("restart roles...")
            restart = Restart(guild)
            restart.roles()

        # copy roles and add to cache memory if you need copy the server tow in run one you have get error
        elif command.startswith(".copy -roles") or command.startswith(".copy -r"):

            guild_id = input("Give me server id: ")
            guild = Guild(guild_id, token)
            if guild.get_info.get("code"):
                print("\033[91mInvalid server id\033[0m")
                continue

            to_guild_id = input("Give me your server id: ")
            to_guild = Guild(to_guild_id, token)
            if to_guild.get_info.get("code"):
                print("\033[91mInvalid server id\033[0m")
                continue

            copy = Copy(guild=guild, to_guild=to_guild)
            copy.create_roles()

        # just copy emojis
        elif command.startswith(".copy -emojis") or command.startswith(".copy -e"):
            guild_id = input("Give me server id: ")
            guild = Guild(guild_id, token)

            if guild.get_info.get("code"):
                print("\033[91mInvalid server id\033[0m")
                continue

            to_guild_id = input("Give me your server id: ")
            to_guild = Guild(to_guild_id, token)
            if to_guild.get_info.get("code"):
                print("\033[91mInvalid server id\033[0m")
                continue

            copy = Copy(guild=guild, to_guild=to_guild)
            copy.create_emojis()

        # to copy: icon, name, description, ...
        elif command.startswith(".copy -settings") or command.startswith(".copy -s"):
            guild_id = input("Give me server id: ")
            guild = Guild(guild_id, token)

            if guild.get_info.get("code"):
                print("\033[91mInvalid server id\033[0m")
                continue

            to_guild_id = input("Give me your server id: ")
            to_guild = Guild()
            if Guild(to_guild_id).get_info.get("code"):
                print("\033[91mInvalid server id\033[0m")
                continue

            copy = Copy(guild=guild, to_guild=to_guild)
            copy.update_settings_from_server()

        # this is a great command to copy all roles, channels, emojis, settings
        # the cache imprtant here because synchronization channel permissions with roles 
        elif command.startswith(".copy -all") or command.startswith(".copy -a"):

            guild_id = input("Give me server id: ")
            guild = Guild(guild_id, token)
            if guild.get_info.get("code"):
                print("\033[91mInvalid server id\033[0m")
                continue

            to_guild_id = input("Give me your server id: ")
            to_guild = Guild(to_guild_id, token)
            if to_guild.get_info.get("code"):
                print("\033[91mInvalid server id\033[0m")
                continue

            copy = Copy(guild=guild, to_guild=to_guild)
            restart = Restart(guild=to_guild)

            print("restart roles...")
            restart.roles()
            print("restart channels...")
            restart.channels()
            print("restart roles...")
            restart.roles()
            print("restart emojis...")
            restart.emojis()
            print("copy roles...")
            copy.create_roles()
            print("copy channels...")
            copy.create_channels()
            print("copy emojis...")
            copy.create_emojis()
            print("copy server settings...")
            copy.update_settings_from_server()

if __name__ == "__main__":
    main()

