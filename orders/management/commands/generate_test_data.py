import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from branches.models import Branch
from clients.models import Client
from orders.models import Order
from services.models import ServiceType


class Command(BaseCommand):
	help = 'Generates test data for the dry cleaning application'

	def add_arguments(self, parser):
		parser.add_argument(
			'--users',
			default=10,
			type=int,
			help='Number of users/clients to create'
		)
		parser.add_argument(
			'--branches',
			default=3,
			type=int,
			help='Number of branches to create'
		)
		parser.add_argument(
			'--services',
			default=15,
			type=int,
			help='Number of service types to create'
		)
		parser.add_argument(
			'--orders',
			default=50,
			type=int,
			help='Number of orders to create'
		)
		parser.add_argument(
			'--reset',
			action='store_true',
			help='Reset the database before generating new data'
		)
		parser.add_argument(
			'--skip-users',
			action='store_true',
			help='Skip user and client creation'
		)
		parser.add_argument(
			'--list-users',
			action='store_true',
			help='List existing users and clients'
		)

	def handle(self, *args, **options):
		num_users = options['users']
		num_branches = options['branches']
		num_services = options['services']
		num_orders = options['orders']
		reset_db = options['reset']
		skip_users = options['skip_users']
		list_users = options['list_users']

		if list_users:
			self.list_users_and_clients()
			return

		self.stdout.write('Generating test data...')

		# Reset database if requested
		if reset_db:
			self.reset_database()

		# Generate branches
		self.create_branches(num_branches)

		# Generate service types
		self.create_services(num_services)

		# Generate users and clients
		if not skip_users:
			self.create_users_and_clients(num_users)
		else:
			self.stdout.write('Skipping user and client creation')

		# Generate orders
		self.create_orders(num_orders)

		self.stdout.write(self.style.SUCCESS('Successfully generated test data!'))
		self.stdout.write(f"Created: {num_branches} branches, {num_services} services, {num_users} users/clients, {num_orders} orders")

	def create_branches(self, count):
		self.stdout.write('Creating branches...')

		# Sample branch data
		branch_names = [
			'Центральный филиал',
			'Северный филиал',
			'Западный филиал',
			'Восточный филиал',
			'Южный филиал',
			'Бизнес-центр',
			'ТЦ Галерея',
			'ТЦ Горизонт',
			'ТЦ Мегамолл',
			'ЖК Солнечный'
		]

		addresses = [
			'ул. Ленина, 15',
			'пр. Мира, 78',
			'ул. Гагарина, 43',
			'ул. Пушкина, 22',
			'пр. Космонавтов, 56',
			'ул. Советская, 12',
			'ул. Дзержинского, 89',
			'пр. Победы, 34',
			'ул. Революции, 67',
			'ул. Строителей, 45'
		]

		# Sample phone numbers
		phone_numbers = [
			'+7 (495) 123-45-67',
			'+7 (812) 234-56-78',
			'+7 (383) 345-67-89',
			'+7 (343) 456-78-90',
			'+7 (831) 567-89-01',
			'+7 (863) 678-90-12',
			'+7 (846) 789-01-23',
			'+7 (351) 890-12-34',
			'+7 (391) 901-23-45',
			'+7 (423) 012-34-56'
		]

		# Sample opening hours
		opening_hours_options = [
			'Пн-Пт: 9:00-19:00, Сб-Вс: 10:00-17:00',
			'Пн-Пт: 8:00-20:00, Сб: 9:00-18:00, Вс: выходной',
			'Ежедневно: 10:00-22:00',
			'Пн-Сб: 8:30-20:30, Вс: 10:00-18:00',
			'Пн-Пт: 9:00-21:00, Сб-Вс: 10:00-20:00',
			'Пн-Пт: 8:00-19:00, Сб: 10:00-16:00, Вс: выходной',
			'Круглосуточно',
			'Пн-Чт: 9:00-20:00, Пт: 9:00-21:00, Сб-Вс: 10:00-18:00',
			'Пн-Вс: 9:00-20:00',
			'Пн-Пт: 7:30-21:30, Сб-Вс: 9:00-19:00'
		]

		for i in range(count):
			name = branch_names[i % len(branch_names)]
			if i >= len(branch_names):
				name = f"{name} #{i // len(branch_names) + 1}"

			branch = Branch.objects.create(
				name=name,
				address=addresses[i % len(addresses)],
				phone=phone_numbers[i % len(phone_numbers)],
				opening_hours=opening_hours_options[i % len(opening_hours_options)]
			)
			self.stdout.write(f'  Created branch: {branch.name} - {branch.phone}')

	def create_services(self, count):
		self.stdout.write('Creating services...')

		# Sample service data
		categories = ['Химчистка', 'Стирка', 'Глажка', 'Ремонт', 'Чистка обуви']

		service_names = {
			'Химчистка': [
				'Химчистка верхней одежды',
				'Химчистка пальто',
				'Химчистка костюма',
				'Химчистка платья',
				'Химчистка пуховика',
				'Химчистка куртки',
				'Химчистка шубы',
				'Химчистка дубленки',
				'Химчистка кожаных изделий',
				'Химчистка замшевых изделий'
			],
			'Стирка': [
				'Стирка белья',
				'Стирка постельного белья',
				'Стирка рубашек',
				'Стирка джинсов',
				'Стирка штор',
				'Стирка пледов',
				'Стирка одеял',
				'Стирка подушек',
				'Стирка спецодежды',
				'Экспресс-стирка'
			],
			'Глажка': [
				'Глажка рубашек',
				'Глажка брюк',
				'Глажка постельного белья',
				'Глажка платья',
				'Глажка пиджака',
				'Глажка блузки',
				'Глажка юбки',
				'Глажка галстука',
				'Глажка костюма',
				'Глажка штор'
			],
			'Ремонт': [
				'Ремонт одежды',
				'Подшивка брюк',
				'Замена молнии',
				'Ремонт карманов',
				'Штопка',
				'Ремонт шубы',
				'Подгонка по фигуре',
				'Укорачивание рукавов',
				'Ремонт воротника',
				'Перекрой изделия'
			],
			'Чистка обуви': [
				'Чистка кожаной обуви',
				'Чистка замшевой обуви',
				'Чистка текстильной обуви',
				'Обновление цвета обуви',
				'Водоотталкивающая пропитка',
				'Чистка сапог',
				'Чистка кроссовок',
				'Глубокая чистка обуви',
				'Удаление соляных разводов',
				'Полировка обуви'
			]
		}

		# Create varied price ranges for different service categories
		price_ranges = {
			'Химчистка': (1000, 5000),
			'Стирка': (300, 1500),
			'Глажка': (200, 800),
			'Ремонт': (300, 2000),
			'Чистка обуви': (300, 1200)
		}

		services_created = 0
		category_index = 0

		while services_created < count:
			category = categories[category_index % len(categories)]
			category_index += 1

			# Get service names for the current category
			names = service_names[category]

			# Get price range for the current category
			min_price, max_price = price_ranges[category]

			# Create services in the current category
			for name in names:
				if services_created >= count:
					break

				base_price = random.randint(min_price, max_price)
				complexity_multiplier = Decimal(str(round(random.uniform(1.0, 1.5), 2)))
				urgency_multiplier = Decimal(str(round(random.uniform(1.0, 1.4), 2)))

				service = ServiceType.objects.create(
					name=name,
					category=category,
					base_price=base_price,
					complexity_multiplier=complexity_multiplier,
					urgency_multiplier=urgency_multiplier
				)

				self.stdout.write(f'  Created service: {service.name} ({service.category}) - {service.base_price} ₽')
				services_created += 1

	def list_users_and_clients(self):
		"""List existing users and clients for diagnostic purposes"""
		self.stdout.write('Existing users:')
		for user in User.objects.all():
			has_client = hasattr(user, 'client')
			client_info = f" (Client ID: {user.client.id})" if has_client else " (No client record)"
			self.stdout.write(f"  User {user.id}: {user.username}{client_info}")

		self.stdout.write('\nExisting clients:')
		for client in Client.objects.all():
			self.stdout.write(f"  Client {client.id}: {client.full_name} (User ID: {client.user_id})")

	def create_users_and_clients(self, count):
		self.stdout.write('Creating users and clients...')

		# Sample name data
		first_names = [
			'Александр', 'Михаил', 'Иван', 'Дмитрий', 'Сергей',
			'Андрей', 'Алексей', 'Максим', 'Евгений', 'Николай',
			'Мария', 'Анна', 'Ольга', 'Елена', 'Наталья',
			'Татьяна', 'Екатерина', 'Светлана', 'Юлия', 'Ирина'
		]

		last_names = [
			'Иванов', 'Смирнов', 'Кузнецов', 'Попов', 'Васильев',
			'Петров', 'Соколов', 'Михайлов', 'Новиков', 'Федоров',
			'Иванова', 'Смирнова', 'Кузнецова', 'Попова', 'Васильева',
			'Петрова', 'Соколова', 'Михайлова', 'Новикова', 'Федорова'
		]

		patronymics = [
			'Александрович', 'Михайлович', 'Иванович', 'Дмитриевич', 'Сергеевич',
			'Андреевич', 'Алексеевич', 'Максимович', 'Евгеньевич', 'Николаевич',
			'Александровна', 'Михайловна', 'Ивановна', 'Дмитриевна', 'Сергеевна',
			'Андреевна', 'Алексеевна', 'Максимовна', 'Евгеньевна', 'Николаевна'
		]

		# Get existing client count
		existing_clients_count = Client.objects.count()

		# If we already have enough clients, we're done
		if existing_clients_count >= count:
			self.stdout.write(f'  Already have {existing_clients_count} clients, no need to create more')
			return

		# Calculate how many more clients we need to create
		clients_to_create = count - existing_clients_count
		self.stdout.write(f'  Creating {clients_to_create} new clients')

		# Create the needed number of user-client pairs
		for i in range(clients_to_create):
			# Create a unique username based on timestamp and counter
			timestamp = int(timezone.now().timestamp())
			username = f"user_{i + 1}_{timestamp}"

			# Determine gender based on index
			is_female = i % 2 == 1

			# Select names based on gender
			if is_female:
				first_name = random.choice(first_names[10:])
				last_name = random.choice(last_names[10:])
				patronymic = random.choice(patronymics[10:])
			else:
				first_name = random.choice(first_names[:10])
				last_name = random.choice(last_names[:10])
				patronymic = random.choice(patronymics[:10])

			# Create contact details
			email = f"{username}@example.com"
			phone = f'+7 9{random.randint(10, 99)} {random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10, 99)}'
			address = f'ул. {random.choice(["Ленина", "Мира", "Гагарина", "Пушкина", "Космонавтов"])}, д. {random.randint(1, 100)}, кв. {random.randint(1, 200)}'

			try:
				# Create user
				user = User.objects.create_user(
					username=username,
					email=email,
					password='password123',
					first_name=first_name,
					last_name=last_name
				)

				# Create client for this user
				client = Client.objects.create(
					user=user,
					first_name=first_name,
					last_name=last_name,
					patronymic=patronymic,
					phone=phone,
					email=email,
					address=address,
					created_at=timezone.now() - timedelta(days=random.randint(0, 365))
				)

				self.stdout.write(f'  Created client #{i + 1}: {client.last_name} {client.first_name} ({username})')
			except Exception as e:
				self.stdout.write(self.style.ERROR(f'  Error creating client #{i + 1}: {str(e)}'))

	def create_orders(self, count):
		self.stdout.write('Creating orders...')

		clients = list(Client.objects.all())
		service_types = list(ServiceType.objects.all())
		branches = list(Branch.objects.all())

		if not clients or not service_types or not branches:
			self.stdout.write(self.style.WARNING('Cannot create orders: missing clients, service types, or branches'))
			return

		status_choices = ['pending', 'in_progress', 'completed', 'cancelled']
		urgency_levels = ['low', 'medium', 'high']
		complexity_levels = ['low', 'medium', 'high']

		for i in range(count):
			client = random.choice(clients)
			service_type = random.choice(service_types)
			branch = random.choice(branches)

			# Randomly distribute status with more weight toward completed
			status_weights = [0.2, 0.2, 0.5, 0.1]  # pending, in_progress, completed, cancelled
			status = random.choices(status_choices, weights=status_weights, k=1)[0]

			# Set received date between 1 day and 60 days ago
			received_at = timezone.now() - timedelta(days=random.randint(1, 60))

			# If status is completed, set a completed date after received date
			completed_at = None
			if status == 'completed':
				days_to_complete = random.randint(1, 5)  # 1-5 days to complete an order
				completed_at = received_at + timedelta(days=days_to_complete)

			# Randomly choose urgency and complexity levels
			urgency_level = random.choice(urgency_levels)
			complexity_level = random.choice(complexity_levels)

			# Calculate price based on service, urgency, complexity and client status
			base_price = service_type.base_price

			# Apply urgency surcharge
			if urgency_level == 'high':
				urgency_surcharge = base_price * Decimal('0.3')  # 30% surcharge
			elif urgency_level == 'medium':
				urgency_surcharge = base_price * Decimal('0.15')  # 15% surcharge
			else:
				urgency_surcharge = Decimal('0')

			# Apply complexity surcharge
			if complexity_level == 'high':
				complexity_surcharge = base_price * Decimal('0.2')  # 20% surcharge
			elif complexity_level == 'medium':
				complexity_surcharge = base_price * Decimal('0.1')  # 10% surcharge
			else:
				complexity_surcharge = Decimal('0')

			# Calculate total price
			total_price = base_price + urgency_surcharge + complexity_surcharge

			# Apply discount for regular customers (3+ orders)
			client_orders_count = Order.objects.filter(client=client).count()
			if client_orders_count >= 2:  # 3rd order or more (after counting this one)
				discount = total_price * Decimal('0.03')  # 3% discount
				total_price -= discount

			# Generate random description
			descriptions = [
				'Сильные загрязнения на воротнике и манжетах.',
				'Пятно от красного вина на передней части.',
				'Необходима срочная чистка к мероприятию.',
				'Требуется особый уход из-за деликатной ткани.',
				'Общее освежение изделия без видимых загрязнений.',
				'Пятна неизвестного происхождения на спине.',
				'Загрязнения по нижнему краю изделия.',
				'Следы от шариковой ручки на кармане.',
				'Требуется восстановление цвета изделия.',
				'Необходимо удалить запах.',
				'Желтизна в области подмышек.',
				None  # Some orders might not have a description
			]

			description = random.choice(descriptions)

			order = Order.objects.create(
				client=client,
				service_type=service_type,
				branch=branch,
				received_at=received_at,
				completed_at=completed_at,
				status=status,
				urgency_level=urgency_level,
				complexity_level=complexity_level,
				final_price=total_price,
				description=description
			)

			self.stdout.write(f'  Created order: #{order.id} - {order.service_type.name} ({order.status}) - {order.final_price:.2f} ₽')

	def reset_database(self):
		"""Clear existing data from the database before adding new data"""
		self.stdout.write('Resetting database...')

		# Delete all orders first (they depend on other models)
		orders_count = Order.objects.count()
		Order.objects.all().delete()
		self.stdout.write(f'  Deleted {orders_count} orders')

		# Delete all clients
		clients_count = Client.objects.count()
		Client.objects.all().delete()
		self.stdout.write(f'  Deleted {clients_count} clients')

		# Delete all regular users (keep superusers)
		users_count = User.objects.filter(is_superuser=False).count()
		User.objects.filter(is_superuser=False).delete()
		self.stdout.write(f'  Deleted {users_count} regular users')

		# Delete all services
		services_count = ServiceType.objects.count()
		ServiceType.objects.all().delete()
		self.stdout.write(f'  Deleted {services_count} services')

		# Delete all branches
		branches_count = Branch.objects.count()
		Branch.objects.all().delete()
		self.stdout.write(f'  Deleted {branches_count} branches')

		self.stdout.write(self.style.SUCCESS('Database reset complete'))
