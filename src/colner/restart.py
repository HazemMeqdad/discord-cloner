from .guild import Guild


class Restart(object):
    def __init__(self, guild: Guild):
        self.guild = guild

    def channels(self):
        if self.guild.get_info.get("code") == 50001:
            print("\033[91mInvalid server id\033[0m")
        for channel in self.guild.channels:
            o = self.guild.delete_channel(channel["id"])
            if "50013" in o:
                print(f"\033[91mMissing Permissions {channel['name']}\033[0m")
                continue
            print(f"\33[90mDelete {channel['name']}\033[0m")

    def roles(self):
        if self.guild.get_info.get("code") == 50001:
            print("\033[91mInvalid server id\033[0m")
        for role in self.guild.roles:
            o = self.guild.delete_role(role["id"])
            if "50013" in o:
                print(f"\033[91mMissing Permissions {role['name']}\033[0m")
                continue
            print(f"\33[90mDelete {role['name']}\033[0m")

    def emojis(self):
        if self.guild.get_info.get("code") == 50001:
            print("\033[91mInvalid server id\033[0m")
        for emoji in self.guild.emojis:
            o = self.guild.delete_emoji(emoji["id"])
            if "50013" in o:
                print(f"\033[91mMissing Permissions {emoji['name']}\033[0m")
                continue
            print(f"\33[90mDelete {emoji['name']}\033[0m")
