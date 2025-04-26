import { api } from './axios'

import type { UserCreate, UserRead} from '../types/users'

export const usersApi = {
    create: (payload: UserCreate) =>
        api.post<UserRead>('/users/create_user', payload).then(res => res.data),
    list: () =>
        api.get<UserRead[]>('/users/query_all_users').then(res => res.data),
};