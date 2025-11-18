export interface FeedBack {
    id: number;
    user_id: number;
    code?: string;
    title_vi?: string;
    disease?: number;
    block?: number;
    chapter?: number;
    status: number;
    reason?: string;
    created_at: string;
}

export interface Status {
    id: number;
    name: string;
    class: string;
    is_list: boolean;
}