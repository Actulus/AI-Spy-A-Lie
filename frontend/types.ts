export type Player = {
    name: string;
    score: number;
    profile: string;
};

export type HighscoreResponse = {
    id: string;
    kinde_uuid: string;
    profile_picture: string;
    user_name: string;
    user_total_score: number;
    created_at: string;
    updated_at: string;
};

export type PersonalStatisticsResponse = {
    match_id:     string;
    match_date:   string;
    user_score:   number;
    opponents:    Opponent[];
    ai_opponents: AIOpponent[];
}

export type AIOpponent = {
    ai_type: string;
    score:   number;
}

export interface Opponent {
    user_name: string;
    score:     number;
}


export type TotalHighscoreResponse = {
    user_total_score: number;
};