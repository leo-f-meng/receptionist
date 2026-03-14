from skills.building_skill import get_building_info
from skills.delivery_skill import delivery_dropoff
from skills.lost_found_skill import check_lost_item, report_found_item, report_lost_item
from skills.visitor_checkin_skill import start_visitor_checkin
from skills.weather_skill import lookup_weather


def reception_skills():
    return [
        lookup_weather,
        get_building_info,
        report_lost_item,
        check_lost_item,
        delivery_dropoff,
        report_found_item,
        start_visitor_checkin,
    ]
