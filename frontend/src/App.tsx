import React from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useUsers } from './hooks/useUsers'
// 👇 uncomment this and point to where you actually put the MUI form
// import MuiCreateUserForm from './components/MuiCreateUserForm'

const queryClient = new QueryClient()

export default function App() {
  const { data: users, isLoading, create } = useUsers()

  function handleCreate(user: {
    user_name: string
    user_age: number
    user_gender: string
    user_role: string
  }) {
    create.mutate(user)
  }

  return (
    <QueryClientProvider client={queryClient}>
      <div style={{ padding: 20 }}>
        <h1>Users</h1>
        {isLoading ? (
          <p>Loading…</p>
        ) : (
          <ul>
            {(users ?? []).map(u => ( 

            // {users?.map(u => (
              <li key={u.user_id}>
                {u.user_name} ({u.user_age}, {u.user_role})
              </li>
            ))}
          </ul>
        )}
        {/* <MuiCreateUserForm onCreate={handleCreate} /> */}
      </div>
    </QueryClientProvider>
  )
}
