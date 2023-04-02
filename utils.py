from discord import CategoryChannel, Guild, TextChannel, VoiceChannel
from discord.utils import get as discord_get

from settings import LOG_TC_NAME, MECA_CATEGORY_NAME, WORKING_ROOM_VC_NAME


def is_meca_category_ch(ch: TextChannel | VoiceChannel | None) -> bool:
    """
    指定したチャンネルがmecaのカテゴリ内に存在するか確認する
    """
    if ch is None:
        return False

    category_name = "None" if ch.category is None else ch.category.name  # categoryがNoneでもAttributeErrorにならないように処理
    if category_name != MECA_CATEGORY_NAME:
        return False
    return True


def is_working_room_vc(vc: VoiceChannel | None) -> bool:
    """
    指定したボイスチャンネルがmecaカテゴリ内に存在する作業用ボイスチャンネルか確認する
    """
    if not is_meca_category_ch(vc):
        return False
    return vc.name == WORKING_ROOM_VC_NAME


def is_log_tc(tc: TextChannel | None) -> bool:
    """
    指定したテキストチャンネルがmecaカテゴリ内に存在するログ出力用テキストチャンネルか確認する
    """
    if not is_meca_category_ch(tc):
        return False
    return tc.name == LOG_TC_NAME


async def get_or_create_meca_category(guild: Guild) -> CategoryChannel:
    """
    指定したサーバー内のmecaカテゴリを取得する(存在しなかった場合は新しく生成する)
    """
    category = discord_get(guild.categories, name=MECA_CATEGORY_NAME)
    if category is None:
        category = await guild.create_category_channel(MECA_CATEGORY_NAME)
    return category


async def get_or_create_working_room_vc(guild: Guild) -> VoiceChannel:
    """
    指定したサーバー内の作業用ボイスチャンネルを取得する(存在しなかった場合は新しく生成する)
    """
    meca_category = await get_or_create_meca_category(guild)

    vc = discord_get(meca_category.voice_channels, name=WORKING_ROOM_VC_NAME)
    if vc is None:
        vc = await meca_category.create_voice_channel(WORKING_ROOM_VC_NAME)
    return vc


async def get_or_create_log_tc(guild: Guild) -> TextChannel:
    """
    指定したサーバー内のログ出力用テキストチャンネルを取得する(存在しなかった場合は新しく生成する)
    """
    meca_category = await get_or_create_meca_category(guild)

    tc = discord_get(meca_category.text_channels, name=LOG_TC_NAME)
    if tc is None:
        tc = await meca_category.create_text_channel(LOG_TC_NAME)
    return tc
