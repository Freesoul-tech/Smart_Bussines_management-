from django.shortcuts import render


FEATURE_ROUTE_MAP = {
    'Guests': '/guests/',
    'Reservations': '/reservations/',
    'Housekeeping': '/housekeeping/',
    'Billing': '/billing/',
    'Reports & Analytics': '/reports-analytics/',
    'Notifications': '/notifications/',
    'Settings': '/settings/',
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
}


REPORT_DATA = {
    'hotel': {
        'revenue': '$24,500',
        'occupancy': '82%',
        'bookings': '128',
        'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'values': [18, 22, 26, 24, 29, 31],
    },
    'restaurant': {
        'revenue': '$12,300',
        'occupancy': '74%',
        'bookings': '96',
        'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
        'values': [15, 18, 20, 17, 25, 28],
    },
}


def _module_route_map(modules):
    routes = {}
    for module in modules:
        routes[module] = FEATURE_ROUTE_MAP.get(module, '#')
    return routes


def index(request):
    business_type = request.GET.get('business_type', 'hotel').lower()
    modules = MODULES.get(business_type, MODULES['hotel'])
    report = REPORT_DATA.get(business_type, REPORT_DATA['hotel'])
    tailoring = BUSINESS_TAILORING.get(business_type, BUSINESS_TAILORING['hotel'])
    context = {
        'business_type': business_type.title(),
        'modules': modules,
        'module_routes': _module_route_map(modules),
        'report': report,
        'tailoring': tailoring,
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


def feature_page(request, slug):
    feature = FEATURE_PAGE_CONTENT.get(slug)
    if feature is None:
        return render(request, 'dashboard/feature_page.html', {'title': 'Page not found'})
    return render(request, 'dashboard/feature_page.html', {
        'page_title': feature['title'],
        'summary': feature['summary'],
        'slug': slug,
    })


def guests(request):
    return feature_page(request, 'guests')


def reservations(request):
    return feature_page(request, 'reservations')


def housekeeping(request):
    return feature_page(request, 'housekeeping')


def billing(request):
    return feature_page(request, 'billing')


def reports_analytics(request):
    return feature_page(request, 'reports-analytics')


def notifications(request):
    return feature_page(request, 'notifications')


def settings(request):
    return feature_page(request, 'settings')
