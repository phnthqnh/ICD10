export interface ChatSession
{
    id?: number;
    user?: User;
    title: string;
    created_at?: string;
}

export interface User
{
    id?: number;
    username?: string;
    email?: string;
    first_name?: string;
    last_name?: string;
    avatar?: string;
}

export interface ChatMessage
{
    id?: number;
    session?: number;
    role?: string;
    content?: string;
    image?: string;
    created_at?: string;
    timestamp?: string;
    isStreaming?: boolean;
}

export interface UserMessage
{
    content: string;
    image?: string;
}

export interface BotMessage
{
    content: string;
    source_type?: string;
}


export interface ChatResponse
{
    session_id?: number;
    intent?: string;
    user_message: UserMessage;
    bot_message: BotMessage;
}