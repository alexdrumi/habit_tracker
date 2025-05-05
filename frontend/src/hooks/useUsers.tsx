import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { usersApi } from '../api/usersApi'
import type { UserCreate, UserRead } from '../types/users'

export function useUsers() {
  const queryClient = useQueryClient()

  const list = useQuery<UserRead[], Error>(['users'], usersApi.list)

  const create = useMutation<UserRead, Error, UserCreate>(
    (newUser: UserCreate) => usersApi.create(newUser),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['users'])
      },
    }
  )

  return { ...list, create }
}