export interface User {
    id: number;
    username: string;
    email: string;
    first_name: string;
    last_name: string;
    avatar?: string;
    status?: number;
    role?: number;
    is_staff?: boolean;
    is_superuser?: boolean;
    last_login?: boolean;
    created_at: string;
    is_verified_doctor?: boolean
    license_number?: string
    hospital?: string
    verification_file?: string
}

export interface Role {
    id: number;
    name: string;
    class: string;
    is_list: boolean;
}