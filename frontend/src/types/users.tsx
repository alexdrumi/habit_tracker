
export interface UserCreate {
    user_name: string;
    user_age: number;
    user_gender: string;
    user_role: string;
}

export interface UserRead {
    user_id: number;
    user_name: string;
    user_age: number;
    user_role: string;
}