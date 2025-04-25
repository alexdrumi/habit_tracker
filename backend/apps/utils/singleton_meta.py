class SingletonMeta(type):
	'''
	A Singleton metaclass that ensures a class has only one instance.
	'''
	_instances = {}

	def __call__(cls, *args, **kwargs): #https://www.geeksforgeeks.org/__call__-in-python/ ->functions like init but for metaclasses
		#cls checks if this class (cls) already, exist in instances
		if cls not in cls._instances:
			instance = super().__call__(*args, **kwargs)
			cls._instances[cls] = instance
		return cls._instances[cls]

