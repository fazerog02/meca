from calendar import monthrange
from datetime import datetime

from discord import Guild, Intents, Member, VoiceState
from discord.ext.commands import Bot, Context

from settings import DISCORD_TOKEN, db
from utils import get_or_create_log_tc, get_or_create_meca_category, get_or_create_working_room_vc, is_working_room_vc

intents = Intents.default()
intents.message_content = True
intents.voice_states = True
bot = Bot(command_prefix="!", intents=intents)


@bot.command()
async def export(ctx: Context, year: int, month: int, mention: str):
    """
    月の総労働時間を出力する
    """
    if month < 1 or month > 12:
        await ctx.send("無効な月です")
        return

    # メンションからmember idを抽出する
    member_id = mention.replace("<", "").replace("@", "").replace("!", "").replace(">", "")

    next_month = month + 1
    next_year = year
    if next_month == 13:
        next_year += 1
        next_month = 1

    search_begin = datetime(year, month, 1, 0, 0, 0).timestamp()
    search_end = datetime(next_year, next_month, 1, 0, 0, 0).timestamp()
    log_snapshots = db.collection("log").where("member_id", "==", member_id).where("started", "<", search_end).order_by("started").stream()

    sum_minutes = 0
    for log in log_snapshots:
        started = log.get("started")
        ended = log.get("ended")

        # 本当はfirestoreのクエリでこの条件を指定したかったが複数フィールドを扱う複合クエリが禁止されている(！)ためここで絞り込みをする
        # 参考: https://firebase.google.com/docs/firestore/query-data/queries?hl=ja#compound_queries
        if ended <= search_begin:
            continue

        # 範囲外まで計算しないように処理
        if started < search_begin:
            started = search_begin
        if ended > search_end:
            ended = search_end

        sum_minutes += int((ended - started) / 60)

    _day, end_date = monthrange(year, month)  # 月の始めと終わりの日付を取得
    await ctx.send(f"{mention}の{year}/{month}/1〜{year}/{month}/{end_date}の労働時間は{int(sum_minutes / 60)}時間{sum_minutes % 60}分です！")


@bot.event
async def on_guild_join(guild: Guild):
    """
    サーバー追加時に必要なチャンネル郡が存在しなければ生成する
    """
    get_or_create_meca_category(guild)
    get_or_create_working_room_vc(guild)
    get_or_create_log_tc(guild)


@bot.event
async def on_voice_state_update(member: Member, before: VoiceState, after: VoiceState):
    """
    作業用VCの入退出を監視して作業時間を計算する
    また，記録した作業ログはfirestoreに保存する
    """
    # vcの移動がなければ終了
    if before.channel == after.channel:
        return

    log_tc = get_or_create_log_tc(member.guild)
    if is_working_room_vc(after.channel):
        # 入室時
        db.collection("status").document(str(member.id)).set({"started": datetime.utcnow().timestamp()})  # firestoreに作業開始時のUTC unix timeを保存
        await log_tc.send(f"{member.mention}が作業を開始しました！")
    elif is_working_room_vc(before.channel):
        # 退出時
        status_snapshot = db.collection("status").document(str(member.id)).get()

        # 作業時間をUTC unix time(秒)の差分から1分単位で計算する
        started = status_snapshot.get("started")
        ended = datetime.utcnow().timestamp()
        work_minutes = int((ended - started) / 60)

        # firestoreの作業開始時間を初期化してログを保存
        db.collection("log").document().set({"started": started, "ended": ended, "member_id": str(member.id)})
        db.collection("status").document(str(member.id)).set({"started": None})

        await log_tc.send(f"{member.mention}が作業を終了しました！")
        await log_tc.send(f"作業時間は{int(work_minutes / 60)}時間{work_minutes % 60}分です　お疲れ様でした！")


if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
