import time;
from datetime import datetime;
import json;
import asyncio;

from TikTokLive import TikTokLiveClient;
from TikTokLive.client.logger import LogLevel;
from TikTokLive.events import ConnectEvent, DisconnectEvent, RoomUserSeqEvent, CommentEvent, GiftEvent, ShareEvent, FollowEvent, LikeEvent;

id: str = "@drmarkz";
brandName: str = "XYZ";
streamerName: str = "streamer1"
streamerID: str = "s6281455"
producersName: str = "producer1"
producerID: str = "p6281455"

data: dict = {
    "liveSessionInfo": {
            "channelName": id,
            "brandName": brandName,
            "streamerName": streamerName,
            "streamerID": streamerID,
            "producerName": producersName,
            "producerID": producerID,
            "sessionStartTime": "",
            "sessionEndTime": "",
            "sessionDuration": "",
        },
    "userActivityOverTime": [],
    "userRetention": {},
    "comments": [],
    "likes": [],
    "shares": [],
    "follows": [],
    "gifts": [],
    };

def update_and_write_to_json(data, filename) -> None:
    # Serialize data to JSON format, ensuring proper encoding of non-ASCII characters
    json_data = json.dumps(data, ensure_ascii = False, indent = 8);

    # Write JSON data to a file with UTF-8 encoding
    with open(filename, 'w', encoding = "utf-8") as file:
        file.write(json_data);

client: TikTokLiveClient = TikTokLiveClient(unique_id = id);

@client.on(ConnectEvent)
async def on_connect(event: ConnectEvent) -> None:
    client.logger.info("Connected!")

    data["liveSessionInfo"]["sessionStartTime"] = f"{datetime.fromtimestamp(time.time())}";

    user_input: str = input("Press Enter to stop the program.");
    if user_input == "":
        await client.disconnect();

@client.on(DisconnectEvent)
async def on_live_end(_: DisconnectEvent) -> None:
    client.logger.info("Disconnected!");

    data["liveSessionInfo"]["sessionEndTime"] = f"{datetime.fromtimestamp(time.time()).isoformat()}";
    start_time = datetime.fromisoformat(data["liveSessionInfo"]["sessionStartTime"])
    end_time = datetime.fromisoformat(data["liveSessionInfo"]["sessionEndTime"])
    data["liveSessionInfo"]["sessionDuration"] = str(end_time - start_time)

    update_and_write_to_json(data, f"{id} data.json");

acc_t_i: int = 0;
curr_t_i: int = 0;
users_time: dict = {};
@client.on(RoomUserSeqEvent)
async def on_count(event: RoomUserSeqEvent) -> None:
    current_time: str = datetime.fromtimestamp(time.time());

    users = event.ranks_list;
    for individual in users:
        user = individual.user.id;
        if user not in users_time:
            users_time[user] = {"joined": f"{current_time}", 
                                "stayedUntil": f"{current_time}"};
        else:
            users_time[user]["stayedUntil"] = f"{current_time}";
    data["userRetention"] = users_time;

    global acc_t_i;
    global curr_t_i;
    acc_t_f: int = event.total_user;
    curr_t_f: int = event.total;
    in_t: int = acc_t_f-acc_t_i;
    out_t: int = in_t-(curr_t_f-curr_t_i);
    acc_t_i, curr_t_i = acc_t_f, curr_t_f;

    # maybe change rankedUsersInRoom len(users_time) to len(event.ranks_list)
    new_flow: dict = {
        "incomingUsers": in_t,
        "outgoingUsers": out_t,
        "accumulatedUsers": acc_t_f,
        "currentUsersInRoom": curr_t_f,
        "timestamp": f"{current_time}"
    }
    data["userActivityOverTime"].append(new_flow);

@client.on(CommentEvent)
async def on_comment(event: CommentEvent) -> None:
    current_time: str = datetime.fromtimestamp(time.time());
    new_comment = {
        "user": event.user.nickname,
        "comment": event.comment,
        "timestamp": f"{current_time}"
        };
    data["comments"].append(new_comment);

@client.on(LikeEvent)
async def on_like(event: LikeEvent):
    current_time: str = datetime.fromtimestamp(time.time());
    new_like = {
        "username": event.user.nickname,
        "userId": event.user.unique_id,
        "timestamp": f"{current_time}"
        };
    data["likes"].append(new_like);

@client.on(ShareEvent)
async def on_share(event: ShareEvent):
    current_time: str = datetime.fromtimestamp(time.time());
    new_share = {
        "username": event.user.nickname,
        "userId": event.user.unique_id,
        "timestamp": f"{current_time}"
        };
    data["shares"].append(new_share);

@client.on(FollowEvent)
async def on_follow(event: FollowEvent):
    current_time: str = datetime.fromtimestamp(time.time());
    new_follow = {
        "username": event.user.nickname,
        "userId": event.user.unique_id,
        "timestamp": f"{current_time}"
        };
    data["follows"].append(new_follow);

@client.on(GiftEvent)
async def on_gift(event: GiftEvent):
    current_time: str = datetime.fromtimestamp(time.time());

    # Can have a streak and streak is over
    if event.gift.streakable and not event.streaking:
        new_gift = {
        "username": event.user.nickname,
        "userId": event.user.unique_id,
        "gift": f"{event.repeat_count}x{event.gift.name}",
        "timestamp": f"{current_time}"
        };
        data["gifts"].append(new_gift);

    # Cannot have a streak
    elif not event.gift.streakable:
        new_gift = {
        "username": event.user.nickname,
        "userId": event.user.unique_id,
        "gift": event.gift.name,
        "timestamp": f"{current_time}"
        };
        data["gifts"].append(new_gift);

async def main():
    if not await client.is_live():
        client.logger.info("Client is currently not live. Please try again later.");
    else:
        client.logger.info("Client is live! Connnecting...");
        await client.connect();

if __name__ == '__main__':
    client.logger.setLevel(LogLevel.INFO.value);
    try:
        asyncio.run(main());
    except KeyboardInterrupt:
        pass;