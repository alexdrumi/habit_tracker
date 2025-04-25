from apps.users.schemas import UserCreate, UserRead

def map_to_user_read_schema(user_info: tuple) -> UserRead:
	#(1, 'FIRST USER', 33, 'user')
	read_schema = UserRead(
		user_id = user_info[0],
		user_name = user_info[1],
		user_age = user_info[2],
		user_role =  user_info[3]
	)
	return read_schema
