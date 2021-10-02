from requests import request
from base64 import b64encode

base = "https://discord.com/api/v9"

class Guild(object):
    def __init__(self, guild_id, token: str, /):
        self.guild_id = guild_id
        self.headers = {"Authorization": token, "Content-Type": "application/json"}

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
            headers=self.headers
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
            headers=self.headers
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
            headers=self.headers
        )
        return re.json()

    def delete_role(self, role_id):
        re = request(
            "DELETE",
            f"{base}/guilds/{self.guild_id}/roles/{role_id}",
            headers=self.headers
        )
        return re.text

    def delete_channel(self, channel_id):
        re = request(
            "DELETE",
            f"{base}/channels/{channel_id}",
            headers=self.headers
        )
        return re.text

    def delete_emoji(self, emoji_id):
        re = request(
            "DELETE",
            f"{base}/guilds/{self.guild_id}/emojis/{emoji_id}",
            headers=self.headers
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
            headers=self.headers
        )

    @property
    def roles(self) -> list:
        re = request(
            "GET",
            f"{base}/guilds/{self.guild_id}/roles",
            headers=self.headers
        )
        json = re.json()
        try:
            json.sort(key=lambda role: role['position'], reverse=True)
            return json
        except:
            return []

    @property
    def channels(self) -> dict:
        re = request(
            "GET",
            f"{base}/guilds/{self.guild_id}/channels",
            headers=self.headers
        )
        return re.json()

    @property
    def emojis(self) -> dict:
        re = request(
            "GET",
            f"{base}/guilds/{self.guild_id}/emojis",
            headers=self.headers
        )
        return re.json()

    @property
    def get_info(self) -> dict:
        re = request(
            "GET",
            f"{base}/guilds/{self.guild_id}",
            headers=self.headers
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
