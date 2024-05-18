export type Player = {
    name: string;
    score: number;
    profile: string;
};

export type HighscoreResponse = {
    id: string;
    highscore_datetime: Date;
    user_name: string;
    user_score: number;
    room_socket_id: string;
    ai_bot_type: string;
    kinde_uuid: string;
    profile_picture: string;
};