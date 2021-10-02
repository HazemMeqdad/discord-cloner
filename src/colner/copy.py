from .guild import Guild
from requests import request
from base64 import b64encode

cache = {}


class Copy(object):
    def __init__(self, guild: Guild, to_guild: Guild):
        self.guild = guild
        self.to_guild = to_guild

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
            if not cache.get("roles"):
                cache["roles"] = {}
            cache["roles"][role["id"]] = new_role["id"]

    def create_channels(self):
        def permission(_channel):
            permission_overwrites = []
            for per in _channel["permission_overwrites"]:
                if per["type"] == 1:
                    continue
                if not cache["roles"].get(per["id"]) and per["id"] == self.guild.default_role["id"]:
                    per["id"] = self.to_guild.default_role["id"]
                    permission_overwrites.append(per)
                    continue
                per["id"] = cache["roles"][per["id"]]
                permission_overwrites.append(per)
            return permission_overwrites

        guild_channels = self.guild.channels
        free_channels = list(filter(lambda cha: cha["type"] != 4 and not cha["parent_id"], guild_channels))
        categorys = list(filter(lambda cha: cha["type"] == 4, guild_channels))
        channels = list(filter(lambda cha: cha["type"] != 4 and cha["parent_id"], guild_channels))
        for channel in free_channels:
            if channel["type"] == 5 and not "COMMUNITY" in self.to_guild.get_info["features"]:
                channel["type"] = 0
            if channel["type"] == 13 and not "COMMUNITY" in self.to_guild.get_info["features"]:
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
            if not cache.get("categorys"):
                cache["categorys"] = {}
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
            cache["categorys"][category["id"]] = new_category["id"]
        for channel in channels:
            if channel["type"] == 5 and not "COMMUNITY" in self.to_guild.get_info["features"]:
                channel["type"] = 0
            if channel["type"] == 13 and not "COMMUNITY" in self.to_guild.get_info["features"]:
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
                parent_id=cache.get("categorys").get(channel["parent_id"]),
                nsfw=channel["nsfw"],
                permission_overwrites=permission(channel)
            )
            if o.get("code"):
                print(f"\033[91mMissing Permissions {channel['name']}\033[0m")
                continue
            print(f"\33[90mCreate channel {channel['name']}\033[0m")
        cache.clear()

    def update_settings_from_server(self):
        guild = self.guild.get_info
        json = {
            "name": guild["name"],
            "verification_level": guild["verification_level"],
            "default_message_notifications": guild["default_message_notifications"],
            "explicit_content_filter": guild["explicit_content_filter"],
            "description": guild["description"],
        }
        self.to_guild.edit_guild(json=json)
        json = {}
        if self.guild.banner_url:
            re = request("GET", self.guild.banner_url).content
            json["banner"] = "data:image/jpeg;" + b64encode(re).decode("utf-8")
        if self.guild.icon_url:
            re = request("GET", self.guild.icon_url).content
            if self.guild.icon_url.endswith(".gif"):
                json["icon"] = f"data:image/gif;base64," + b64encode(re).decode("utf-8")
            elif self.guild.icon_url.endswith(".png"):
                json["icon"] = f"data:image/png;base64," + b64encode(re).decode("utf-8")
            elif self.guild.icon_url.endswith(".jpeg"):
                json["icon"] = f"data:image/jpeg;base64," + b64encode(re).decode("utf-8")
        if not json:
            return
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
