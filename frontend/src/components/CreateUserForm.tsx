import { FormEvent, useState} from "react";
import type { UserCreate } from "../types/users";


interface Props {
    onCreate: (data: UserCreate) => void;
}


export default function CreateUserForm({ onCreate}: Props) {
    const [user_name, setName] = useState("");
    const [user_age, setAge] = useState(0);
    const [user_gender, setGender] = useState("");
    const [user_role, setRole] = useState("");


    function handleSubmit(e: FormEvent) {
        e.preventDefault();

        onCreate({ user_name, user_age, user_gender, user_role });
        setName(""); setAge(0); setGender(""); setRole("");
    }

    return (
        <form onSubmit={handleSubmit}>
          <input
            placeholder="Name"
            value={user_name}
            onChange={e => setName(e.target.value)}
            required
          />
          <input
            type="number"
            placeholder="Age"
            value={user_age || ""}
            onChange={e => setAge(Number(e.target.value))}
            required
          />
          <input
            placeholder="Gender"
            value={user_gender}
            onChange={e => setGender(e.target.value)}
            required
          />
          <input
            placeholder="Role"
            value={user_role}
            onChange={e => setRole(e.target.value)}
            required
          />
          <button type="submit">Create User</button>
        </form>
      );
}