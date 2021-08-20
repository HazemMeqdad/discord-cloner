from requests import request
from base64 import b64encode
from time import sleep
from os import getenv

token = getenv("token")
base = "https://discord.com/api/v9"
headers = {"Authorization": token, "Content-Type": "application/json"}

data = {}


class Guild(object):
    def __init__(self, guild_id):
        self.guild_id = guild_id

    def create_role(
            self,
            name: str = "new role",
            permissions: str = "0",
            color: int = 0,
            hoist: bool = False,
            mentionable: bool = False
    ) -> dict:
        re = request(
            "POST",
            f"{base}/guilds/{self.guild_id}/roles",
            json={
                "name": name,
                "permissions": permissions,
                "color": color,
                "hoist": hoist,
                "mentionable": mentionable
            },
            headers=headers
        )
        return re.json()

    def create_channel(
            self,
            name: str,
            type: int,
            topic: str = None,
            bitrate: int = None,
            user_limit: int = None,
            rate_limit_per_user: int = None,
            position: int = None,
            parent_id=None,
            nsfw=False,
            permission_overwrites: list = None
    ) -> dict:
        """
        GUILD_TEXT	            0	    a text channel within a server
        GUILD_VOICE	            2	    a voice channel within a server
        GUILD_CATEGORY	        4	    an organizational category that contains up to 50 channels
        GUILD_NEWS	            5	    a channel that users can follow and crosspost into their own server
        GUILD_STORE	            6	    a channel in which game developers can sell their game on Discord
        GUILD_STAGE_VOICE	    13	    a voice channel for hosting events with an audience
        """
        json = {
            "name": name,
            "type": type,
            "topic": topic,
            "rate_limit_per_user": rate_limit_per_user,
            "position": position,
            "parent_id": parent_id,
            "nsfw": nsfw
        }
        if permission_overwrites:
            json["permission_overwrites"] = permission_overwrites
        if type == 2:
            if bitrate:
                json["bitrate"] = bitrate
            if user_limit:
                json["user_limit"] = user_limit
        re = request(
            "POST",
            f"{base}/guilds/{self.guild_id}/channels",
            json=json,
            headers=headers
        )
        return re.json()

    def create_emoji(
        self,
        name: str,
        url: str,
    ) -> dict:
        image = "data:image/jpeg;base64," + b64encode(request("GET", url).content).decode("utf-8")
        re = request(
            "POST",
            f"{base}/guilds/{self.guild_id}/emojis",
            json={
                "name": name,
                "image": image,
                "roles": []
            },
            headers=headers
        )
        return re.json()

    def delete_role(self, role_id):
        re = request(
            "DELETE",
            f"{base}/guilds/{self.guild_id}/roles/{role_id}",
            headers=headers
        )
        return re.text

    @staticmethod
    def delete_channel(channel_id):
        re = request(
            "DELETE",
            f"{base}/channels/{channel_id}",
            headers=headers
        )
        return re.text

    def delete_emoji(self, emoji_id):
        re = request(
            "DELETE",
            f"{base}/guilds/{self.guild_id}/emojis/{emoji_id}",
            headers=headers
        )
        return re.text

    def edit_guild(
        self,
        json: dict
    ):
        """
        example for data json:
        json = {
            "name": name,
            "region": region,
            "verification_level": verification_level,
            "default_message_notifications": default_message_notifications,
            "explicit_content_filter": explicit_content_filter,
            "afk_channel_id": afk_channel_id,
            "afk_timeout": afk_timeout,
            "icon_url": icon_url,
            "description": description
        }
        """
        request(
            "PATCH",
            f"{base}/guilds/{self.guild_id}",
            json=json,
            headers=headers
        )

    @property
    def roles(self) -> list:
        re = request(
            "GET",
            f"{base}/guilds/{self.guild_id}/roles",
            headers=headers
        )
        json = re.json()
        if "code" in re.text:
            return []
        json.sort(key=lambda role: role['position'], reverse=True)
        return json

    @property
    def channels(self) -> dict:
        re = request(
            "GET",
            f"{base}/guilds/{self.guild_id}/channels",
            headers=headers
        )
        return re.json()

    @property
    def emojis(self) -> dict:
        re = request(
            "GET",
            f"{base}/guilds/{self.guild_id}/emojis",
            headers=headers
        )
        return re.json()

    @property
    def get_info(self) -> dict:
        re = request(
            "GET",
            f"{base}/guilds/{self.guild_id}",
            headers=headers
        )
        return re.json()

    @property
    def default_role(self) -> dict:
        return [role for role in self.roles if role["name"] == "@everyone"][0]

    @property
    def banner_url(self):
        if not self.get_info.get('banner'):
            return None
        return f"https://cdn.discordapp.com/banners/{self.guild_id}/{self.get_info.get('banner')}.webp"

    @property
    def icon_url(self):
        icon = self.get_info.get('icon')
        if not icon:
            return None
        extension = ".png"
        if icon.startswith("a_"):
            extension = ".gif"
        return f"https://cdn.discordapp.com/icons/{self.guild_id}/{self.get_info.get('icon')}{extension}"


class Copy(object):
    def __init__(self, guild_id, to_guild_id):
        self.guild = Guild(guild_id=guild_id)
        self.to_guild = Guild(guild_id=to_guild_id)

    def create_roles(self):
        roles = self.guild.roles
        for role in roles:
            if role["name"] == "@everyone":
                continue
            new_role = self.to_guild.create_role(
                name=role["name"],
                permissions=role["permissions"],
                color=role["color"],
                hoist=role["hoist"],
                mentionable=role["mentionable"]
            )
            if new_role.get("code"):
                print(f"\033[91mMissing Permissions {role['name']}\033[0m")
                continue
            print(f"\33[90mCreate role {role['name']}\033[0m")
            if not data.get("roles"):
                data["roles"] = {}
            data["roles"][role["id"]] = new_role["id"]

    def create_channels(self):
        def permission(_channel):
            permission_overwrites = []
            for per in _channel["permission_overwrites"]:
                if per["type"] == 1:
                    continue
                if not data["roles"].get(per["id"]) and per["id"] == self.guild.default_role["id"]:
                    per["id"] = self.to_guild.default_role["id"]
                    permission_overwrites.append(per)
                    continue
                per["id"] = data["roles"][per["id"]]
                permission_overwrites.append(per)
            return permission_overwrites

        guild_channels = self.guild.channels
        free_channels = list(filter(lambda cha: cha["type"] != 4 and not cha["parent_id"], guild_channels))
        categorys = list(filter(lambda cha: cha["type"] == 4, guild_channels))
        channels = list(filter(lambda cha: cha["type"] != 4 and cha["parent_id"], guild_channels))
        for channel in free_channels:
            if channel["type"] == 5 and not self.to_guild.get_info["features"].get("COMMUNITY"):
                channel["type"] = 0
            if channel["type"] == 13 and not self.to_guild.get_info["features"].get("COMMUNITY"):
                channel["type"] = 2
            if channel["type"] == 10 or channel["type"] == 11 and channel["type"] == 12 and channel["type"] == 6:
                channel["type"] = 0
            o = self.to_guild.create_channel(
                name=channel["name"],
                type=channel["type"],
                topic=channel.get("topic"),
                bitrate=channel.get("bitrate"),
                user_limit=channel.get("user_limit"),
                rate_limit_per_user=channel.get("rate_limit_per_user"),
                position=channel["position"],
                nsfw=channel["nsfw"],
                permission_overwrites=permission(channel)
            )
            if o.get("code"):
                print(f"\033[91mMissing Permissions {channel['name']}\033[0m")
                continue
            print(f"\33[90mCreate channel {channel['name']}\033[0m")
        for category in categorys:
            if not data.get("categorys"):
                data["categorys"] = {}
            new_category = self.to_guild.create_channel(
                name=category["name"],
                type=category["type"],
                topic=category.get("topic"),
                bitrate=category.get("bitrate"),
                user_limit=category.get("user_limit"),
                rate_limit_per_user=category.get("rate_limit_per_user"),
                position=category["position"],
                nsfw=category["nsfw"],
                permission_overwrites=permission(category)
            )
            if new_category.get("code"):
                print(f"\033[91mMissing Permissions {category['name']}\033[0m")
                continue
            print(f"\33[90mCreate category {category['name']}\033[0m")
            data["categorys"][category["id"]] = new_category["id"]
        for channel in channels:
            if channel["type"] == 5 and not self.to_guild.get_info["features"].get("COMMUNITY"):
                channel["type"] = 0
            if channel["type"] == 13 and not self.to_guild.get_info["features"].get("COMMUNITY"):
                channel["type"] = 2
            if channel["type"] == 10 or channel["type"] == 11 and channel["type"] == 12 and channel["type"] == 6:
                channel["type"] = 0
            o = self.to_guild.create_channel(
                name=channel["name"],
                type=channel["type"],
                topic=channel.get("topic"),
                bitrate=channel.get("bitrate"),
                user_limit=channel.get("user_limit"),
                rate_limit_per_user=channel.get("rate_limit_per_user"),
                position=channel["position"],
                parent_id=data.get("categorys").get(channel["parent_id"]),
                nsfw=channel["nsfw"],
                permission_overwrites=permission(channel)
            )
            if o.get("code"):
                print(f"\033[91mMissing Permissions {channel['name']}\033[0m")
                continue
            print(f"\33[90mCreate channel {channel['name']}\033[0m")

    def update_settings_from_server(self):
        guild = self.guild.get_info
        json = {
            "name": guild["name"],
            "verification_level": guild["verification_level"],
            "default_message_notifications": guild["default_message_notifications"],
            "explicit_content_filter": guild["explicit_content_filter"],
            "description": guild["description"],
        }
        if self.guild.banner_url:
            re = request("GET", self.guild.banner_url).content
            json["banner"] = "data:image/jpeg;" + b64encode(re).decode("utf-8")
        if self.guild.icon_url:
            content_type = ["image/jpeg", "image/png", "image/gif"]
            re = request("GET", self.guild.icon_url).content
            if self.guild.icon_url.endswith(".gif"):
                json["icon"] = f"data:{content_type[2]};base64," + b64encode(re).decode("utf-8")
            elif self.guild.icon_url.endswith(".png"):
                json["icon"] = f"data:{content_type[1]};base64," + b64encode(re).decode("utf-8")
            elif self.guild.icon_url.endswith(".jpeg"):
                json["icon"] = f"data:{content_type[0]};base64," + b64encode(re).decode("utf-8")
        self.to_guild.edit_guild(json=json)

    def create_emojis(self):
        emojis = self.guild.emojis
        for emoji in emojis:
            extension = ".png"
            if emoji["animated"]:
                extension = ".gif"
            o = self.to_guild.create_emoji(
                name=emoji["name"],
                url=f"https://cdn.discordapp.com/emojis/{emoji['id']}{extension}"
            )
            if o.get("code"):
                print(f"\033[91mMissing Permissions {emoji['name']}\033[0m")
                continue
            print(f"\33[90mCreate emoji {emoji['name']}\033[0m")


class Restart(object):
    def __init__(self, guild_id):
        self.guild_id = guild_id

    def channels(self):
        guild = Guild(self.guild_id)
        if guild.get_info.get("code") == 50001:
            print("\033[91mInvalid server id\033[0m")
        for channel in guild.channels:
            o = guild.delete_channel(channel["id"])
            if "50013" in o:
                print(f"\033[91mMissing Permissions {channel['name']}\033[0m")
                continue
            print(f"\33[90mDelete {channel['name']}\033[0m")

    def roles(self):
        guild = Guild(self.guild_id)
        if guild.get_info.get("code") == 50001:
            print("\033[91mInvalid server id\033[0m")
        for role in guild.roles:
            o = guild.delete_role(role["id"])
            if "50013" in o:
                print(f"\033[91mMissing Permissions {role['name']}\033[0m")
                continue
            print(f"\33[90mDelete {role['name']}\033[0m")

    def emojis(self):
        guild = Guild(self.guild_id)
        if guild.get_info.get("code") == 50001:
            print("\033[91mInvalid server id\033[0m")
        for emoji in guild.emojis:
            o = guild.delete_emoji(emoji["id"])
            if "50013" in o:
                print(f"\033[91mMissing Permissions {emoji['name']}\033[0m")
                continue
            print(f"\33[90mDelete {emoji['name']}\033[0m")


def main():
    words = "\x1b[6;30;42m[ This tool made by: H A Z E M#1629 ]\x1b[0m\nhttps://github.com/HazemMeqdad\n"
    for char in words:
        sleep(0.1)
        print(char, end='', flush=True)
    commands: dict = {
        "restart": {
            ".restart -all",
            ".restart -emojis",
            ".restart -roles",
            ".restart -channels"
        },
        "copy": {
            ".copy -all",
            ".copy -channels",
            ".copy -roles",
            ".copy -emojis",
            ".copy -settings"
        },
        "exit": {
            ".exit"
        }
    }
    stats = True
    print("====================================================")
    while stats:
        command = input("Enter command more info \033[91m.help\033[0m >>> ")
        if command.startswith(".exit"):
            stats = False
            exit(-1)
        elif command.startswith(".info") or command.startswith(".help"):
            print("Copyright: https://github.com/HazemMeqdad")
            z = ""
            for com, d in commands.items():
                z += com + "\n"
                for i in d:
                    z += "  " + i + "\n"
            print(z)
        elif command.startswith(".restart -roles") or command.startswith(".restart -r"):
            guild_id = input("Give me server id: ")
            if Guild(guild_id).get_info.get("code"):
                print("\033[91mInvalid server id\033[0m")
                continue
            print("restart roles...")
            Restart(command).roles()
        elif command.startswith(".restart -channels") or command.startswith(".restart -c"):
            guild_id = input("Give me server id: ")
            if Guild(guild_id).get_info.get("code"):
                print("\033[91mInvalid server id\033[0m")
                continue
            print("restart channels...")
            Restart(guild_id).channels()
        elif command.startswith(".restart -emojis") or command.startswith(".restart -e"):
            guild_id = input("Give me server id: ")
            if Guild(guild_id).get_info.get("code"):
                print("\033[91mInvalid server id\033[0m")
                continue
            print("restart emojis...")
            Restart(guild_id).emojis()
        elif command.startswith(".restart -all") or command.startswith(".restart -a"):
            guild_id = input("Give me server id: ")
            if Guild(guild_id).get_info.get("code"):
                print("\033[91mInvalid server id\033[0m")
                continue
            o = Restart(guild_id)
            print("restart roles...")
            o.roles()
            print("restart channels...")
            o.channels()
            print("restart emojis...")
            o.emojis()
        elif command.startswith(".copy -roles") or command.startswith(".copy -r"):
            guild_id = input("Give me server id: ")
            if Guild(guild_id).get_info.get("code"):
                print("\033[91mInvalid server id\033[0m")
                continue
            to_guild_id = input("Give me your server id: ")
            if Guild(to_guild_id).get_info.get("code"):
                print("\033[91mInvalid server id\033[0m")
                continue
            Copy(guild_id=guild_id, to_guild_id=to_guild_id).create_roles()
        elif command.startswith(".copy -channels") or command.startswith(".copy -c"):
            guild_id = input("Give me server id: ")
            if Guild(guild_id).get_info.get("code"):
                print("\033[91mInvalid server id\033[0m")
                continue
            to_guild_id = input("Give me your server id: ")
            if Guild(to_guild_id).get_info.get("code"):
                print("\033[91mInvalid server id\033[0m")
                continue
            Copy(guild_id=guild_id, to_guild_id=to_guild_id).create_channels()
        elif command.startswith(".copy -emojis") or command.startswith(".copy -e"):
            guild_id = input("Give me server id: ")
            if Guild(guild_id).get_info.get("code"):
                print("\033[91mInvalid server id\033[0m")
                continue
            to_guild_id = input("Give me your server id: ")
            if Guild(to_guild_id).get_info.get("code"):
                print("\033[91mInvalid server id\033[0m")
                continue
            Copy(guild_id=guild_id, to_guild_id=to_guild_id).create_emojis()
        elif command.startswith(".copy -settings") or command.startswith(".copy -s"):
            guild_id = input("Give me server id: ")
            if Guild(guild_id).get_info.get("code"):
                print("\033[91mInvalid server id\033[0m")
                continue
            to_guild_id = input("Give me your server id: ")
            if Guild(to_guild_id).get_info.get("code"):
                print("\033[91mInvalid server id\033[0m")
                continue
            Copy(guild_id=guild_id, to_guild_id=to_guild_id).update_settings_from_server()
        elif command.startswith(".copy -all") or command.startswith(".copy -a"):
            guild_id = input("Give me server id: ")
            if Guild(guild_id).get_info.get("code"):
                print("\033[91mInvalid server id\033[0m")
                continue
            to_guild_id = input("Give me your server id: ")
            if Guild(to_guild_id).get_info.get("code"):
                print("\033[91mInvalid server id\033[0m")
                continue
            o = Copy(guild_id=guild_id, to_guild_id=to_guild_id)
            r = Restart(guild_id=to_guild_id)
            print("restart roles...")
            r.roles()
            print("restart channels...")
            r.channels()
            print("restart roles...")
            r.roles()
            print("restart emojis...")
            r.emojis()
            print("copy roles...")
            o.create_roles()
            print("copy channels...")
            o.create_channels()
            print("copy emojis...")
            o.create_emojis()
            print("copy server settings...")
            o.update_settings_from_server()


main()
