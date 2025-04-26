import { useQuery, useMutation, useQueryClient} from "react-query";
import { usersApi } from "../api/usersApi";
import type { UserCreate, UserRead } from "../types/users";

export function useUsers() {
    const queryClient = useQueryClient()

    const list = useQuery<UserRead[]>("users", usersApi.list);

    const create = useMutation<UserRead, Error, UserCreate>(
        (newUser) => usersApi.create(newUser),
        {
            onSuccess: () => {
                queryClient.invalidateQueries("users")
            },
        }
    );

    return { ...list, create};
}