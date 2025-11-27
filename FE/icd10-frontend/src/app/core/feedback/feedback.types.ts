export interface FeedBack {
    id: number;
    user: number;
    code?: string;
    title_vi?: string;
    disease?: any;
    block?: any;
    chapter?: any;
    disease_parent?: any;
    new_chapter?: any;
    new_block?: any;
    new_disease_parent?: any;
    status: number;
    reason?: string;
    created_at: string;
}

export interface FeedBackResponse {
    chapter_feedbacks: FeedBack[];
    block_feedbacks: FeedBack[];
    disease_feedbacks: FeedBack[];
}

export interface Status {
    id: number;
    name: string;
    class: string;
    is_list: boolean;
}