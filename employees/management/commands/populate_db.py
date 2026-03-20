from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
import random
from authentication.models import User
from departments.models import Department, Position
from employees.models import Employee, EducationRecord, WorkExperience
from attendance.models import AttendanceRecord, Holiday, WorkSchedule
from leave_management.models import LeaveType, LeaveBalance, LeaveRequest
from payroll.models import PayrollPeriod, Payslip, AllowanceType, EmployeeAllowance, Bonus
from recruitment.models import JobPosting, Candidate, Application, Interview, Offer
from performance.models import PerformanceReviewCycle, Goal, PerformanceReview, Feedback, TrainingProgram, TrainingEnrollment

class Command(BaseCommand):
    help = 'Populates the database with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting database population...')

        # Clear existing data (optional)
        self.stdout.write('Clearing existing data...')
        Employee.objects.all().delete()
        Department.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

        # Create Departments
        self.stdout.write('Creating departments...')
        departments_data = [
            {'name': 'Engineering', 'description': 'Software development and engineering'},
            {'name': 'Marketing', 'description': 'Marketing and brand management'},
            {'name': 'Sales', 'description': 'Sales and business development'},
            {'name': 'Human Resources', 'description': 'HR and talent management'},
            {'name': 'Finance', 'description': 'Finance and accounting'},
            {'name': 'Operations', 'description': 'Operations and logistics'},
        ]
        
        departments = {}
        for dept_data in departments_data:
            dept = Department.objects.create(**dept_data)
            departments[dept.name] = dept
            self.stdout.write(f'Created department: {dept.name}')

        # Create Positions
        self.stdout.write('Creating positions...')
        positions_data = {
            'Engineering': ['Junior Developer', 'Senior Developer', 'Team Lead', 'Engineering Manager'],
            'Marketing': ['Marketing Coordinator', 'Marketing Manager', 'Brand Manager'],
            'Sales': ['Sales Representative', 'Sales Manager', 'Account Executive'],
            'Human Resources': ['HR Coordinator', 'HR Manager', 'Recruiter'],
            'Finance': ['Accountant', 'Financial Analyst', 'Finance Manager'],
            'Operations': ['Operations Coordinator', 'Operations Manager'],
        }

        positions = {}
        for dept_name, position_titles in positions_data.items():
            positions[dept_name] = []
            for title in position_titles:
                pos = Position.objects.create(
                    title=title,
                    department=departments[dept_name],
                    description=f'{title} position in {dept_name}'
                )
                positions[dept_name].append(pos)
                self.stdout.write(f'Created position: {title}')

        # Create Users and Employees
        self.stdout.write('Creating employees...')
        
        first_names = ['John', 'Sarah', 'Michael', 'Emily', 'David', 'Jessica', 'Daniel', 'Ashley', 
                       'James', 'Jennifer', 'Robert', 'Linda', 'William', 'Patricia', 'Richard',
                       'Maria', 'Thomas', 'Nancy', 'Christopher', 'Lisa', 'Matthew', 'Karen',
                       'Joshua', 'Betty', 'Andrew', 'Helen', 'Ryan', 'Sandra', 'Brian', 'Donna']
        
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
                      'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson',
                      'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'White', 'Harris']

        cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia',
                  'San Antonio', 'San Diego', 'Dallas', 'San Jose']

        employment_types = ['FULL_TIME', 'FULL_TIME', 'FULL_TIME', 'PART_TIME', 'CONTRACT']
        genders = ['M', 'F']
        marital_statuses = ['SINGLE', 'MARRIED', 'MARRIED', 'SINGLE']

        employees_list = []
        employee_count = 0

        for dept_name, dept in departments.items():
            dept_positions = positions[dept_name]
            
            # Create 6-12 employees per department
            num_employees = random.randint(6, 12)
            
            for i in range(num_employees):
                employee_count += 1
                first_name = random.choice(first_names)
                last_name = random.choice(last_names)
                email = f'{first_name.lower()}.{last_name.lower()}{employee_count}@company.com'
                
                # Create User
                user = User.objects.create_user(
                    email=email,
                    password='password123',
                    first_name=first_name,
                    last_name=last_name,
                    role=random.choice(['EMPLOYEE', 'EMPLOYEE', 'EMPLOYEE', 'MANAGER'])
                )

                # Create Employee
                position = random.choice(dept_positions)
                base_salary = random.randint(40000, 150000)
                
                employee = Employee.objects.create(
                    user=user,
                    employee_id=f'EMP{str(employee_count).zfill(4)}',
                    department=dept,
                    position=position,
                    date_of_birth=datetime(random.randint(1980, 2000), random.randint(1, 12), random.randint(1, 28)).date(),
                    gender=random.choice(genders),
                    marital_status=random.choice(marital_statuses),
                    nationality='USA',
                    personal_email=f'{first_name.lower()}{last_name.lower()}@gmail.com',
                    emergency_contact_name=f'{random.choice(first_names)} {random.choice(last_names)}',
                    emergency_contact_phone=f'+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}',
                    emergency_contact_relation=random.choice(['Spouse', 'Parent', 'Sibling']),
                    address_line1=f'{random.randint(100, 9999)} Main Street',
                    city=random.choice(cities),
                    state='CA',
                    postal_code=f'{random.randint(10000, 99999)}',
                    country='USA',
                    employment_type=random.choice(employment_types),
                    date_of_joining=(timezone.now() - timedelta(days=random.randint(30, 1095))).date(),
                    basic_salary=base_salary,
                    is_active=random.choice([True, True, True, True, False])
                )
                
                employees_list.append(employee)
                self.stdout.write(f'Created employee: {employee.employee_id} - {user.get_full_name()}')

        # Assign managers
        self.stdout.write('Assigning managers...')
        for dept_name, dept in departments.items():
            dept_employees = Employee.objects.filter(department=dept, is_active=True)
            if dept_employees.count() > 1:
                manager = dept_employees.first()
                manager.user.role = 'MANAGER'
                manager.user.save()
                dept.manager = manager.user
                dept.save()
                
                # Assign manager to other employees
                for emp in dept_employees[1:]:
                    emp.manager = manager
                    emp.save()

        # Create Leave Types
        self.stdout.write('Creating leave types...')
        leave_types_data = [
            {'name': 'Annual Leave', 'default_days_per_year': 20, 'is_paid': True, 'color_code': '#3498db'},
            {'name': 'Sick Leave', 'default_days_per_year': 10, 'is_paid': True, 'color_code': '#e74c3c'},
            {'name': 'Casual Leave', 'default_days_per_year': 7, 'is_paid': True, 'color_code': '#2ecc71'},
            {'name': 'Unpaid Leave', 'default_days_per_year': 30, 'is_paid': False, 'color_code': '#95a5a6'},
        ]
        
        leave_types = []
        for lt_data in leave_types_data:
            lt = LeaveType.objects.create(**lt_data)
            leave_types.append(lt)
            self.stdout.write(f'Created leave type: {lt.name}')

        # Create Leave Balances for all employees
        self.stdout.write('Creating leave balances...')
        current_year = timezone.now().year
        for employee in employees_list:
            for leave_type in leave_types:
                LeaveBalance.objects.create(
                    employee=employee,
                    leave_type=leave_type,
                    year=current_year,
                    total_days=leave_type.default_days_per_year,
                    used_days=random.randint(0, 5),
                    remaining_days=leave_type.default_days_per_year - random.randint(0, 5)
                )

        # Create some Leave Requests
        self.stdout.write('Creating leave requests...')
        for _ in range(20):
            employee = random.choice(employees_list)
            leave_type = random.choice(leave_types)
            start_date = timezone.now().date() + timedelta(days=random.randint(1, 60))
            end_date = start_date + timedelta(days=random.randint(1, 5))
            
            LeaveRequest.objects.create(
                employee=employee,
                leave_type=leave_type,
                start_date=start_date,
                end_date=end_date,
                total_days=(end_date - start_date).days + 1,
                reason='Personal reasons',
                status=random.choice(['PENDING', 'APPROVED', 'APPROVED', 'REJECTED'])
            )

        # Create Holidays
        self.stdout.write('Creating holidays...')
        holidays_data = [
            {'name': 'New Year', 'date': datetime(2025, 1, 1).date()},
            {'name': 'Independence Day', 'date': datetime(2025, 7, 4).date()},
            {'name': 'Christmas', 'date': datetime(2025, 12, 25).date()},
        ]
        
        for holiday_data in holidays_data:
            Holiday.objects.create(**holiday_data)

        # Create Attendance Records
        self.stdout.write('Creating attendance records...')
        for employee in employees_list[:20]:  # First 20 employees
            for i in range(30):  # Last 30 days
                date = (timezone.now() - timedelta(days=i)).date()
                if date.weekday() < 5:  # Monday to Friday
                    AttendanceRecord.objects.create(
                        employee=employee,
                        date=date,
                        check_in=datetime.strptime('09:00', '%H:%M').time(),
                        check_out=datetime.strptime('18:00', '%H:%M').time(),
                        status='PRESENT'
                    )

        # Create Job Postings
        self.stdout.write('Creating job postings...')
        job_titles = [
            'Senior Software Engineer',
            'Marketing Manager',
            'Sales Executive',
            'HR Manager',
            'Financial Analyst'
        ]
        
        for title in job_titles:
            dept = random.choice(list(departments.values()))
            JobPosting.objects.create(
                title=title,
                department=dept,
                job_type='FULL_TIME',
                description=f'We are looking for a talented {title} to join our team.',
                requirements='Bachelor degree, 3+ years experience',
                responsibilities='Lead projects, mentor team members, deliver results',
                min_salary=60000,
                max_salary=120000,
                location='Remote',
                number_of_openings=random.randint(1, 3),
                status='OPEN'
            )

        # Create Candidates
        self.stdout.write('Creating candidates...')
        for i in range(15):
            first = random.choice(first_names)
            last = random.choice(last_names)
            Candidate.objects.create(
                first_name=first,
                last_name=last,
                email=f'{first.lower()}.{last.lower()}@email.com',
                phone=f'+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}',
                current_company='Tech Corp',
                current_position='Developer',
                total_experience_years=random.randint(1, 10)
            )

        # Create Performance Review Cycle
        self.stdout.write('Creating performance review cycle...')
        PerformanceReviewCycle.objects.create(
            name='Q4 2024 Performance Review',
            cycle_type='QUARTERLY',
            start_date=datetime(2024, 10, 1).date(),
            end_date=datetime(2024, 12, 31).date(),
            review_deadline=datetime(2025, 1, 15).date(),
            is_active=True
        )

        # Create Training Programs
        self.stdout.write('Creating training programs...')
        training_data = [
            {'name': 'Leadership Training', 'duration_hours': 20},
            {'name': 'Technical Skills Workshop', 'duration_hours': 16},
            {'name': 'Communication Skills', 'duration_hours': 8},
        ]
        
        for training in training_data:
            TrainingProgram.objects.create(
                name=training['name'],
                description=f'Professional development program for {training["name"]}',
                instructor='External Trainer',
                start_date=timezone.now().date() + timedelta(days=30),
                end_date=timezone.now().date() + timedelta(days=35),
                duration_hours=training['duration_hours'],
                max_participants=20,
                location='Conference Room A',
                status='PLANNED'
            )

        self.stdout.write(self.style.SUCCESS('Successfully populated database!'))
        self.stdout.write(f'Created {employee_count} employees across {len(departments)} departments')