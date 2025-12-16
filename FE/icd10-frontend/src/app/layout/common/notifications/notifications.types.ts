export interface Notification
{
    id: string;
    icon?: string;
    image?: string;
    title?: string;
    description?: string;
    time: string;
    link?: string;
    useRouter?: boolean;
    read: boolean;
    notifications?: any;
    unread_count?: number;
    is_read?: boolean;
    created_at?: string;
    message?: string;
    notif_type?: string;
    url?: string;
}
