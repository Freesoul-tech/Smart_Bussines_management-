from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render


FEATURE_ROUTE_MAP = {
    'Guests': '/guests/',
    'Reservations': '/reservations/',
    'Housekeeping': '/housekeeping/',
    'Billing': '/billing/',
    'Reports & Analytics': '/reports-analytics/',
    'Notifications': '/notifications/',
    'Settings': '/settings/',
    # Alias entries so similar module names link to existing feature pages
    'Customers': '/guests/',
}


CORE_MODULES = [
    'Authentication & Role Management',
    'Dashboard',
    'Customers',
    'Inventory',
    'Suppliers',
    'Procurement',
    'Sales/ Sales and Point of Sale (POS)',
    'Expenses',
    'Reports & Analytics',
    'Notifications',
    'Settings',
]

SUPPORTED_BUSINESS_TYPES = [
    'Hotel',
    'Motel',
    'Lodge',
    'Guest House',
    'Restaurant',
    'Bakery',
    'Pub/Bar',
    'Boutique',
]

BUSINESS_TAILORING = {
    'hotel': {
        'headline': 'Hotel Business',
        'summary': 'Manage reservations, rooms, guests, billing, and service quality in one elegant workspace.',
        'focus': ['Reservations', 'Room Management', 'Housekeeping', 'Billing'],
        'visual': {
            'image': 'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=900&q=80',
            'title': 'Luxury stay operations',
            'caption': 'Room readiness, arrivals, and guest delight in one polished hub.',
            'background': 'linear-gradient(135deg, rgba(79,70,229,0.18), rgba(20,184,166,0.14))',
        },
    },
    'restaurant': {
        'headline': 'Restaurant Business',
        'summary': 'Coordinate orders, tables, inventory, and team performance across every shift.',
        'focus': ['Table Management', 'Kitchen Orders', 'POS', 'Menu Management'],
        'visual': {
            'image': 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=900&q=80',
            'title': 'Kitchen flow & service',
            'caption': 'Track orders, seating, and meal prep with calm precision.',
            'background': 'linear-gradient(135deg, rgba(239,68,68,0.16), rgba(251,191,36,0.14))',
        },
    },
    'bakery': {
        'headline': 'Bakery Business',
        'summary': 'Track production, ingredient flow, customer orders, and daily operations from one control center.',
        'focus': ['Production Planning', 'Recipe Management', 'Ingredient Inventory', 'Daily Production'],
        'visual': {
            'image': 'https://images.unsplash.com/photo-1483695028939-5bb13f8648b0?auto=format&fit=crop&w=900&q=80',
            'title': 'Fresh-bake production',
            'caption': 'Keep batches, recipes, and deliveries beautifully on schedule.',
            'background': 'linear-gradient(135deg, rgba(251,191,36,0.18), rgba(249,115,22,0.14))',
        },
    },
    'motel': {
        'headline': 'Motel Business',
        'summary': 'Keep overnight stays, check-ins, and maintenance simple, fast, and reliable.',
        'focus': ['Quick Check-ins', 'Room Readiness', 'Guest Support', 'Maintenance'],
        'visual': {
            'image': 'https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=900&q=80',
            'title': 'Roadside hospitality',
            'caption': 'Streamline arrivals and housekeeping for quick-turn stays.',
            'background': 'linear-gradient(135deg, rgba(14,165,233,0.16), rgba(59,130,246,0.12))',
        },
    },
    'lodge': {
        'headline': 'Lodge Business',
        'summary': 'Blend comfort, bookings, and guest services for a memorable stay.',
        'focus': ['Guest Reservations', 'Housekeeping', 'Activity Planning', 'Guest Experience'],
        'visual': {
            'image': 'https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=900&q=80',
            'title': 'Nature escape operations',
            'caption': 'Coordinate cabins, guides, and guest comfort with ease.',
            'background': 'linear-gradient(135deg, rgba(16,185,129,0.16), rgba(6,182,212,0.12))',
        },
    },
    'guest house': {
        'headline': 'Guest House Business',
        'summary': 'Deliver warm hospitality with flexible bookings and personalized guest care.',
        'focus': ['Guest Profiles', 'Reservations', 'Home Services', 'Reviews'],
        'visual': {
            'image': 'https://images.unsplash.com/photo-1460317442991-0ec209397118?auto=format&fit=crop&w=900&q=80',
            'title': 'Home-style hosting',
            'caption': 'Balance comfort, bookings, and personal touches beautifully.',
            'background': 'linear-gradient(135deg, rgba(249,115,22,0.16), rgba(34,197,94,0.12))',
        },
    },
    'pub/bar': {
        'headline': 'Pub/Bar Business',
        'summary': 'Drive evening service, inventory flow, and guest energy from one live dashboard.',
        'focus': ['Bar Operations', 'Table Service', 'Inventory', 'Events'],
        'visual': {
            'image': 'https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?auto=format&fit=crop&w=900&q=80',
            'title': 'Nightlife momentum',
            'caption': 'Keep drinks, stock, and service moving smoothly after hours.',
            'background': 'linear-gradient(135deg, rgba(139,92,246,0.16), rgba(236,72,153,0.12))',
        },
    },
    'boutique': {
        'headline': 'Boutique Business',
        'summary': 'Manage curated products, sales, and customer experience with accuracy and style.',
        'focus': ['Product Catalog', 'Stock Levels', 'POS', 'Customer Loyalty'],
        'visual': {
            'image': 'https://images.unsplash.com/photo-1529139574466-a303027c1d8b?auto=format&fit=crop&w=900&q=80',
            'title': 'Retail elegance',
            'caption': 'Showcase products, stock, and transactions in a refined view.',
            'background': 'linear-gradient(135deg, rgba(236,72,153,0.16), rgba(79,70,229,0.12))',
        },
    },
}

MODULES = {
    'hotel': [
        'Customers',
        'Inventory',
        'Suppliers',
        'Reservations',
        'Housekeeping',
        'Billing',
        'Sales/ Sales and Point of Sale (POS)',
        'Reports & Analytics',
        'Notifications',
        'Settings',
    ],
    'restaurant': [
        'Customers',
        'Inventory',
        'Procurement',
        'Expenses',
        'Kitchen Operations',
        'Table Management',
        'POS',
        'Reports & Analytics',
        'Notifications',
        'Settings',
    ],
    'bakery': [
        'Customers',
        'Procurement',
        'Production Planning',
        'Recipe Management',
        'Ingredient Inventory',
        'Packaging',
        'Reports & Analytics',
        'Notifications',
        'Settings',
    ],
    'motel': [
        'Reservations',
        'Housekeeping',
        'Billing',
        'Maintenance',
        'Guest Communications',
        'Reports & Analytics',
        'Notifications',
        'Settings',
    ],
    'lodge': [
        'Reservations',
        'Housekeeping',
        'Guest Services',
        'Inventory',
        'Reports & Analytics',
        'Notifications',
        'Settings',
    ],
    'guest house': [
        'Guests',
        'Reservations',
        'Housekeeping',
        'Billing',
        'Reports & Analytics',
        'Notifications',
        'Settings',
    ],
    'pub/bar': [
        'Customers',
        'Inventory',
        'Bar Operations',
        'Order Management',
        'Expenses',
        'Reports & Analytics',
        'Notifications',
        'Settings',
    ],
    'boutique': [
        'Customers',
        'Inventory',
        'POS',
        'Product Catalog',
        'Orders',
        'Marketing',
        'Reports & Analytics',
        'Notifications',
        'Settings',
    ],
}

REPORT_DATA = {
    'hotel': {
        'revenue': 'MK 24,500,000',
        'occupancy': '82%',
        'bookings': '128',
        'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'values': [18, 22, 26, 24, 29, 31],
    },
    'restaurant': {
        'revenue': 'MK 12,300,000',
        'occupancy': '74%',
        'bookings': '96',
        'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
        'values': [15, 18, 20, 17, 25, 28],
    },
    'bakery': {
        'revenue': 'MK 8,900,000',
        'occupancy': '68%',
        'bookings': '84',
        'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
        'values': [12, 14, 13, 16, 18, 20],
    },
    'motel': {
        'revenue': 'MK 11,200,000',
        'occupancy': '76%',
        'bookings': '104',
        'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'values': [14, 16, 17, 19, 20, 22],
    },
    'lodge': {
        'revenue': 'MK 9,750,000',
        'occupancy': '71%',
        'bookings': '88',
        'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'values': [10, 12, 13, 14, 16, 17],
    },
    'guest house': {
        'revenue': 'MK 7,640,000',
        'occupancy': '69%',
        'bookings': '72',
        'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'values': [9, 10, 12, 13, 14, 15],
    },
    'pub/bar': {
        'revenue': 'MK 15,600,000',
        'occupancy': '81%',
        'bookings': '112',
        'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
        'values': [16, 18, 19, 22, 24, 26],
    },
    'boutique': {
        'revenue': 'MK 13,450,000',
        'occupancy': '77%',
        'bookings': '90',
        'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'values': [11, 13, 15, 17, 18, 20],
    },
}


def _module_route_map(modules):
    routes = {}
    for module in modules:
        routes[module] = FEATURE_ROUTE_MAP.get(module, '#')
    return routes


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not username or not password:
            error = 'Please enter both your username and password.'
        else:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.POST.get('next') or 'dashboard:index'
                return redirect(next_url)
            error = 'Invalid username or password.'

    return render(request, 'dashboard/login.html', {'error': error})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    error = None
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        username = request.POST.get('username', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        User = get_user_model()

        if not first_name or not last_name or not email or not username or not password1 or not password2:
            error = 'Please complete all required fields.'
        elif password1 != password2:
            error = 'Passwords do not match.'
        elif User.objects.filter(username__iexact=username).exists():
            error = 'This username is already in use.'
        elif User.objects.filter(email__iexact=email).exists():
            error = 'This email is already registered.'
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name,
            )
            user = authenticate(request, username=username, password=password1)
            if user is not None:
                login(request, user)
                return redirect('dashboard:index')
            error = 'Unable to log in after registration. Please try again.'

    return render(request, 'dashboard/login.html', {'register_error': error, 'show_register': True})


def logout_view(request):
    logout(request)
    return redirect('dashboard:login')


def landing(request):
    return render(request, 'dashboard/landing.html')


@login_required(login_url='dashboard:login')
def index(request):
    selected_business = (
        request.POST.get('business_type')
        or request.GET.get('business_type', '')
        or request.session.get('selected_business_type', '')
    ).strip().lower()

    if selected_business:
        request.session['selected_business_type'] = selected_business
    elif 'selected_business_type' in request.session:
        del request.session['selected_business_type']

    profile = request.session.get('business_profile') or {}
    error = None

    if request.method == 'POST' and request.POST.get('business_name'):
        business_name = request.POST.get('business_name', '').strip()
        business_location = request.POST.get('business_location', '').strip()
        business_email = request.POST.get('business_email', '').strip()
        business_requirements = request.POST.get('business_requirements', '').strip()

        if not business_name or not business_location or not business_email:
            error = 'Please complete your business name, address, and email before continuing.'
        else:
            profile = {
                'business_type': selected_business,
                'business_name': business_name,
                'business_location': business_location,
                'business_email': business_email,
                'business_requirements': business_requirements,
            }
            request.session['business_profile'] = profile

    profile_complete = bool(
        profile.get('business_name')
        and profile.get('business_location')
        and profile.get('business_email')
    )

    if not selected_business:
        context = {
            'business_type': '',
            'business_key': '',
            'modules': [],
            'module_routes': {},
            'report': {
                'revenue': 'Choose a model',
                'occupancy': '--',
                'bookings': '--',
                'labels': ['Hotel', 'Restaurant', 'Boutique'],
                'values': [10, 12, 8],
            },
            'tailoring': {
                'headline': 'Select a business model',
                'summary': 'Choose the business type that matches your operation to unlock the right modules and workflow.',
                'focus': ['Hotel', 'Restaurant', 'Boutique'],
                'visual': {
                    'image': 'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=900&q=80',
                    'title': 'Supported business models',
                    'caption': 'Select the model that best fits how your business operates.',
                    'background': 'linear-gradient(135deg, rgba(15,118,110,0.14), rgba(245,158,11,0.10))',
                },
            },
            'supported_business_types': SUPPORTED_BUSINESS_TYPES,
            'requires_business_selection': True,
        }
        return render(request, 'dashboard/index.html', context)

    if not profile_complete:
        context = {
            'business_type': selected_business.title(),
            'business_key': selected_business,
            'supported_business_types': SUPPORTED_BUSINESS_TYPES,
            'requires_business_selection': False,
            'requires_business_profile': True,
            'business_profile': profile,
            'profile_error': error,
            'tailoring': BUSINESS_TAILORING.get(selected_business, BUSINESS_TAILORING['hotel']),
        }
        return render(request, 'dashboard/index.html', context)

    selected_modules = MODULES.get(selected_business, MODULES['hotel'])
    modules = CORE_MODULES + [m for m in selected_modules if m not in CORE_MODULES]
    report = REPORT_DATA.get(selected_business, REPORT_DATA['hotel'])
    tailoring = BUSINESS_TAILORING.get(selected_business, BUSINESS_TAILORING['hotel'])
    context = {
        'business_type': selected_business.title(),
        'business_key': selected_business,
        'modules': modules,
        'module_routes': _module_route_map(modules),
        'report': report,
        'tailoring': tailoring,
        'supported_business_types': SUPPORTED_BUSINESS_TYPES,
        'requires_business_selection': False,
        'requires_business_profile': False,
        'business_profile': profile,
    }
    return render(request, 'dashboard/index.html', context)


FEATURE_PAGE_CONTENT = {
    'guests': {
        'title': 'Guests',
        'summary': 'Manage guest profiles, check-in details, and personalized service moments from one streamlined page.',
    },
    'reservations': {
        'title': 'Reservations',
        'summary': 'Review bookings, check availability, and keep room or table allocation aligned across the team.',
    },
    'housekeeping': {
        'title': 'Housekeeping',
        'summary': 'Coordinate room readiness, task progress, and daily housekeeping priorities with confidence.',
    },
    'billing': {
        'title': 'Billing',
        'summary': 'Track invoices, transactions, balance updates, and payments in a clean billing workflow.',
    },
    'reports-analytics': {
        'title': 'Reports & Analytics',
        'summary': 'Surface business performance and trend insights with ready-to-share reporting views.',
    },
    'notifications': {
        'title': 'Notifications',
        'summary': 'Keep teams aware of alerts, updates, and follow-ups through a dedicated notification hub.',
    },
    'settings': {
        'title': 'Settings',
        'summary': 'Adjust business preferences, workflow defaults, and account-level controls from a single settings surface.',
    },
}


@login_required(login_url='dashboard:login')
def feature_page(request, slug):
    feature = FEATURE_PAGE_CONTENT.get(slug)
    if feature is None:
        return render(request, 'dashboard/feature_page.html', {'title': 'Page not found'})
    return render(request, 'dashboard/feature_page.html', {
        'page_title': feature['title'],
        'summary': feature['summary'],
        'slug': slug,
    })


@login_required(login_url='dashboard:login')
def guests(request):
    return feature_page(request, 'guests')


@login_required(login_url='dashboard:login')
def reservations(request):
    return feature_page(request, 'reservations')


@login_required(login_url='dashboard:login')
def housekeeping(request):
    return feature_page(request, 'housekeeping')


@login_required(login_url='dashboard:login')
def billing(request):
    return feature_page(request, 'billing')


@login_required(login_url='dashboard:login')
def reports_analytics(request):
    return feature_page(request, 'reports-analytics')


@login_required(login_url='dashboard:login')
def notifications(request):
    return feature_page(request, 'notifications')


@login_required(login_url='dashboard:login')
def settings(request):
    return render(request, 'dashboard/feature_page.html', {
        'page_title': 'Settings',
        'summary': 'Adjust business preferences, workflow defaults, and account-level controls from a single settings surface. Delete your account below when you are ready to permanently remove your profile.',
        'slug': 'settings',
        'show_delete_account': True,
        'user': request.user,
    })


@login_required(login_url='dashboard:login')
def delete_account(request):
    if request.method == 'POST':
        confirm_value = request.POST.get('confirm', '').strip()
        if confirm_value == 'DELETE':
            user = request.user
            logout(request)
            user.delete()
            return redirect('dashboard:login')
        return render(request, 'dashboard/feature_page.html', {
            'page_title': 'Settings',
            'summary': 'Account deletion requires confirmation. Please type DELETE in the confirmation field to continue.',
            'slug': 'settings',
            'show_delete_account': True,
            'user': request.user,
            'delete_error': 'Confirmation failed. Type DELETE to permanently delete your account.',
        })

    return redirect('dashboard:settings')
