from core.access import get_user_business


BUSINESS_MODEL_NAMES = {
    "hotel": "Hotel",
    "motel": "Motel",
    "lodge": "Lodge",
    "guest_house": "Guest House",
    "restaurant": "Restaurant",
    "bakery": "Bakery",
    "pub_bar": "Pub / Bar",
    "boutique": "Boutique",
}


def sbms_business_context(request):

    context = {
        "business": None,
        "business_model": "",
        "business_model_name": "Business",
        "is_accommodation": False,
        "is_food_business": False,
        "is_pub_bar": False,
        "is_boutique": False,
    }

    if not request.user.is_authenticated:
        return context

    business = get_user_business(request.user)

    if not business:
        return context

    business_model = business.business_model or ""

    context.update({
        "business": business,

        "business_model": business_model,

        "business_model_name": BUSINESS_MODEL_NAMES.get(
            business_model,
            "Business",
        ),

        "is_accommodation": business_model in [
            "hotel",
            "motel",
            "lodge",
            "guest_house",
        ],

        "is_food_business": business_model in [
            "restaurant",
            "bakery",
        ],

        "is_pub_bar": business_model == "pub_bar",

        "is_boutique": business_model == "boutique",

        "show_employees": request.user.has_perm("employees.view_employee") or business.owner_id == request.user.id,
        "show_rooms": request.user.has_perm("rooms.view_room") or business.owner_id == request.user.id,
        "show_reservations": request.user.has_perm("reservations.view_reservation") or business.owner_id == request.user.id,
        "show_payments": request.user.has_perm("payments.view_payment") or business.owner_id == request.user.id,
        "show_motel": business_model == "motel" and (request.user.has_perm("motel.view_vehicle") or business.owner_id == request.user.id),
        "show_lodge": business_model == "lodge" and (request.user.has_perm("lodge.view_lodgeunit") or business.owner_id == request.user.id),
        "show_customers": request.user.has_perm("customers.view_customer") or business.owner_id == request.user.id,
        "show_reports": request.user.has_perm("settings_app.view_reports") or business.owner_id == request.user.id,
        "show_settings": request.user.has_perm("settings_app.view_businesssettings") or business.owner_id == request.user.id,
    })

    return context