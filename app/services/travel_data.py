from datetime import datetime, timedelta
from app.services.providers import TravelDataProvider
from app.models.travel import TravelLeg, AvailabilityStatus


def get_all_travel_legs(
    travel_date: datetime | None = None
) -> list[TravelLeg]:

    if travel_date is None:
        travel_date = datetime.now()

    # Use midnight of the requested travel date so that all
    # synthetic journeys are generated relative to that date.
    base_date = travel_date.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    )

    def dt(
        hour: int,
        minute: int = 0,
        day_offset: int = 0
    ) -> datetime:
        return base_date + timedelta(
            days=day_offset,
            hours=hour,
            minutes=minute
        )

    legs = [

        # ==================================================
        # JAMMU → DELHI
        # ==================================================

        TravelLeg(
            origin="Jammu",
            destination="Jammu Airport",
            mode="taxi",
            operator="Jammu Cabs",
            departure_time=dt(14, 0),
            arrival_time=dt(14, 40),
            duration_minutes=40,
            price=400
        ),

        TravelLeg(
            origin="Jammu",
            destination="Delhi",
            mode="flight",
            operator="Premium Airlines",
            departure_time=dt(17, 0),
            arrival_time=dt(18, 30),
            duration_minutes=90,
            price=5000
        ),

        TravelLeg(
            origin="Jammu",
            destination="Delhi",
            mode="train",
            operator="Northern Express",
            departure_time=dt(15, 0),
            arrival_time=dt(19, 0),
            duration_minutes=240,
            price=1200
        ),

        TravelLeg(
            origin="Jammu",
            destination="Delhi",
            mode="bus",
            operator="State Express",
            departure_time=dt(16, 0),
            arrival_time=dt(20, 30),
            duration_minutes=270,
            price=900
        ),

        TravelLeg(
            origin="Jammu",
            destination="Delhi",
            mode="flight",
            operator="Budget Airlines",
            departure_time=dt(18, 0),
            arrival_time=dt(19, 30),
            duration_minutes=90,
            price=3000
        ),

        # ==================================================
        # JAMMU → CHANDIGARH
        # ==================================================

        TravelLeg(
            origin="Jammu",
            destination="Chandigarh",
            mode="train",
            operator="Northern Express",
            departure_time=dt(15, 0),
            arrival_time=dt(19, 0),
            duration_minutes=240,
            price=1200
        ),

        TravelLeg(
            origin="Jammu",
            destination="Chandigarh",
            mode="bus",
            operator="State Express",
            departure_time=dt(16, 0),
            arrival_time=dt(20, 30),
            duration_minutes=270,
            price=900
        ),

        TravelLeg(
            origin="Jammu",
            destination="Chandigarh",
            mode="train",
            operator="Himalayan Express",
            departure_time=dt(13, 30),
            arrival_time=dt(17, 0),
            duration_minutes=210,
            price=1500
        ),

        # ==================================================
        # JAMMU → AMRITSAR
        # ==================================================

        TravelLeg(
            origin="Jammu",
            destination="Amritsar",
            mode="train",
            operator="Punjab Express",
            departure_time=dt(14, 0),
            arrival_time=dt(17, 30),
            duration_minutes=210,
            price=800
        ),

        TravelLeg(
            origin="Jammu",
            destination="Amritsar",
            mode="bus",
            operator="Punjab Roadways",
            departure_time=dt(15, 0),
            arrival_time=dt(19, 0),
            duration_minutes=240,
            price=600
        ),

        # ==================================================
        # JAMMU AIRPORT → DELHI AIRPORT
        # ==================================================

        TravelLeg(
            origin="Jammu Airport",
            destination="Delhi Airport",
            mode="flight",
            operator="Budget Airlines",
            departure_time=dt(17, 30),
            arrival_time=dt(19, 20),
            duration_minutes=110,
            price=3000
        ),

        TravelLeg(
            origin="Jammu Airport",
            destination="Delhi Airport",
            mode="flight",
            operator="Example Airlines",
            departure_time=dt(18, 0),
            arrival_time=dt(19, 30),
            duration_minutes=90,
            price=4000
        ),

        TravelLeg(
            origin="Jammu Airport",
            destination="Delhi Airport",
            mode="flight",
            operator="Premium Airlines",
            departure_time=dt(16, 30),
            arrival_time=dt(18, 10),
            duration_minutes=100,
            price=4500
        ),

        # ==================================================
        # CHANDIGARH → DELHI
        # ==================================================

        TravelLeg(
            origin="Chandigarh",
            destination="Delhi",
            mode="train",
            operator="Shatabdi Express",
            departure_time=dt(19, 30),
            arrival_time=dt(22, 30),
            duration_minutes=180,
            price=900
        ),

        TravelLeg(
            origin="Chandigarh",
            destination="Delhi",
            mode="bus",
            operator="InterCity Bus",
            departure_time=dt(21, 0),
            arrival_time=dt(1, 0, 1),
            duration_minutes=240,
            price=700
        ),

        TravelLeg(
            origin="Chandigarh",
            destination="Delhi",
            mode="flight",
            operator="Regional Airlines",
            departure_time=dt(20, 0),
            arrival_time=dt(21, 0),
            duration_minutes=60,
            price=2500
        ),

        TravelLeg(
            origin="Chandigarh",
            destination="Delhi",
            mode="train",
            operator="InterCity Express",
            departure_time=dt(18, 0),
            arrival_time=dt(21, 15),
            duration_minutes=195,
            price=700
        ),

        # ==================================================
        # AMRITSAR → DELHI
        # ==================================================

        TravelLeg(
            origin="Amritsar",
            destination="Delhi",
            mode="train",
            operator="Golden Express",
            departure_time=dt(18, 0),
            arrival_time=dt(23, 0),
            duration_minutes=300,
            price=1100
        ),

        TravelLeg(
            origin="Amritsar",
            destination="Delhi",
            mode="flight",
            operator="Regional Airlines",
            departure_time=dt(18, 30),
            arrival_time=dt(19, 40),
            duration_minutes=70,
            price=2800
        ),

        TravelLeg(
            origin="Amritsar",
            destination="Delhi",
            mode="bus",
            operator="Punjab Roadways",
            departure_time=dt(19, 0),
            arrival_time=dt(0, 30, 1),
            duration_minutes=330,
            price=800
        ),

        # ==================================================
        # DELHI → JAIPUR
        # ==================================================

        TravelLeg(
            origin="Delhi",
            destination="Jaipur",
            mode="train",
            operator="Pink City Express",
            departure_time=dt(19, 30),
            arrival_time=dt(23, 0),
            duration_minutes=210,
            price=900
        ),

        TravelLeg(
            origin="Delhi",
            destination="Jaipur",
            mode="bus",
            operator="Rajasthan Roadways",
            departure_time=dt(20, 0),
            arrival_time=dt(1, 0, 1),
            duration_minutes=300,
            price=600
        ),

        TravelLeg(
            origin="Delhi",
            destination="Jaipur",
            mode="flight",
            operator="Regional Airlines",
            departure_time=dt(20, 30),
            arrival_time=dt(21, 25),
            duration_minutes=55,
            price=3000
        ),

        # ==================================================
        # JAIPUR → MUMBAI
        # ==================================================

        TravelLeg(
            origin="Jaipur",
            destination="Mumbai",
            mode="flight",
            operator="Western Airlines",
            departure_time=dt(23, 30),
            arrival_time=dt(1, 30, 1),
            duration_minutes=120,
            price=4500
        ),

        TravelLeg(
            origin="Jaipur",
            destination="Mumbai",
            mode="train",
            operator="Rajputana Express",
            departure_time=dt(22, 0),
            arrival_time=dt(10, 0, 1),
            duration_minutes=720,
            price=1800
        ),

        # ==================================================
        # DELHI → MUMBAI
        # ==================================================

        TravelLeg(
            origin="Delhi",
            destination="Mumbai",
            mode="flight",
            operator="Metro Airlines",
            departure_time=dt(20, 0),
            arrival_time=dt(22, 15),
            duration_minutes=135,
            price=4500
        ),

        TravelLeg(
            origin="Delhi",
            destination="Mumbai",
            mode="train",
            operator="Rajdhani Express",
            departure_time=dt(20, 30),
            arrival_time=dt(8, 30, 1),
            duration_minutes=720,
            price=2500
        ),

        TravelLeg(
            origin="Delhi",
            destination="Mumbai",
            mode="flight",
            operator="Budget Airlines",
            departure_time=dt(21, 0),
            arrival_time=dt(23, 20),
            duration_minutes=140,
            price=3800
        ),

        TravelLeg(
            origin="Delhi",
            destination="Mumbai",
            mode="train",
            operator="Central Express",
            departure_time=dt(18, 30),
            arrival_time=dt(7, 30, 1),
            duration_minutes=780,
            price=1800
        ),

        # ==================================================
        # DELHI → AHMEDABAD
        # ==================================================

        TravelLeg(
            origin="Delhi",
            destination="Ahmedabad",
            mode="flight",
            operator="Western Airlines",
            departure_time=dt(20, 0),
            arrival_time=dt(21, 40),
            duration_minutes=100,
            price=4200
        ),

        TravelLeg(
            origin="Delhi",
            destination="Ahmedabad",
            mode="train",
            operator="Gujarat Express",
            departure_time=dt(19, 0),
            arrival_time=dt(7, 0, 1),
            duration_minutes=720,
            price=1600
        ),

        TravelLeg(
            origin="Delhi",
            destination="Ahmedabad",
            mode="bus",
            operator="Western Roadways",
            departure_time=dt(18, 0),
            arrival_time=dt(10, 0, 1),
            duration_minutes=960,
            price=1200
        ),

        # ==================================================
        # AHMEDABAD → MUMBAI
        # ==================================================

        TravelLeg(
            origin="Ahmedabad",
            destination="Mumbai",
            mode="flight",
            operator="Western Airlines",
            departure_time=dt(23, 0),
            arrival_time=dt(0, 15, 1),
            duration_minutes=75,
            price=3000
        ),

        TravelLeg(
            origin="Ahmedabad",
            destination="Mumbai",
            mode="train",
            operator="Western Express",
            departure_time=dt(21, 0),
            arrival_time=dt(5, 30, 1),
            duration_minutes=510,
            price=1000
        ),

        TravelLeg(
            origin="Ahmedabad",
            destination="Mumbai",
            mode="bus",
            operator="Gujarat Roadways",
            departure_time=dt(20, 0),
            arrival_time=dt(7, 0, 1),
            duration_minutes=660,
            price=800
        ),

        # ==================================================
        # DELHI → LUCKNOW
        # ==================================================

        TravelLeg(
            origin="Delhi",
            destination="Lucknow",
            mode="flight",
            operator="North Airlines",
            departure_time=dt(20, 0),
            arrival_time=dt(21, 15),
            duration_minutes=75,
            price=3500
        ),

        TravelLeg(
            origin="Delhi",
            destination="Lucknow",
            mode="train",
            operator="Gomti Express",
            departure_time=dt(19, 0),
            arrival_time=dt(7, 0, 1),
            duration_minutes=720,
            price=1400
        ),

        TravelLeg(
            origin="Delhi",
            destination="Lucknow",
            mode="bus",
            operator="UP Roadways",
            departure_time=dt(18, 30),
            arrival_time=dt(7, 30, 1),
            duration_minutes=780,
            price=1000
        ),

        # ==================================================
        # LUCKNOW → KOLKATA
        # ==================================================

        TravelLeg(
            origin="Lucknow",
            destination="Kolkata",
            mode="flight",
            operator="Eastern Airlines",
            departure_time=dt(23, 0),
            arrival_time=dt(1, 0, 1),
            duration_minutes=120,
            price=4500
        ),

        TravelLeg(
            origin="Lucknow",
            destination="Kolkata",
            mode="train",
            operator="Eastern Express",
            departure_time=dt(20, 0),
            arrival_time=dt(15, 0, 1),
            duration_minutes=1140,
            price=2200
        ),

        # ==================================================
        # DELHI → BANGALORE
        # ==================================================

        TravelLeg(
            origin="Delhi",
            destination="Bangalore",
            mode="flight",
            operator="South Airlines",
            departure_time=dt(21, 0),
            arrival_time=dt(23, 45),
            duration_minutes=165,
            price=5500
        ),

        TravelLeg(
            origin="Delhi",
            destination="Bangalore",
            mode="flight",
            operator="Budget Airlines",
            departure_time=dt(19, 30),
            arrival_time=dt(22, 30),
            duration_minutes=180,
            price=4200
        ),

        TravelLeg(
            origin="Delhi",
            destination="Bangalore",
            mode="train",
            operator="Karnataka Express",
            departure_time=dt(18, 0),
            arrival_time=dt(20, 0, 1),
            duration_minutes=1560,
            price=2800
        ),

        # ==================================================
        # BANGALORE → CHENNAI
        # ==================================================

        TravelLeg(
            origin="Bangalore",
            destination="Chennai",
            mode="flight",
            operator="South Airlines",
            departure_time=dt(23, 30),
            arrival_time=dt(0, 30, 1),
            duration_minutes=60,
            price=2500
        ),

        TravelLeg(
            origin="Bangalore",
            destination="Chennai",
            mode="train",
            operator="Southern Express",
            departure_time=dt(21, 0),
            arrival_time=dt(6, 0, 1),
            duration_minutes=540,
            price=900
        ),

        # ==================================================
        # DELHI → HYDERABAD
        # ==================================================

        TravelLeg(
            origin="Delhi",
            destination="Hyderabad",
            mode="flight",
            operator="Deccan Airlines",
            departure_time=dt(20, 30),
            arrival_time=dt(22, 45),
            duration_minutes=135,
            price=4800
        ),

        TravelLeg(
            origin="Delhi",
            destination="Hyderabad",
            mode="train",
            operator="Deccan Express",
            departure_time=dt(17, 30),
            arrival_time=dt(16, 0, 1),
            duration_minutes=1350,
            price=2400
        ),

        # ==================================================
        # HYDERABAD → BANGALORE
        # ==================================================

        TravelLeg(
            origin="Hyderabad",
            destination="Bangalore",
            mode="flight",
            operator="Deccan Airlines",
            departure_time=dt(23, 30),
            arrival_time=dt(0, 45, 1),
            duration_minutes=75,
            price=2800
        ),

        TravelLeg(
            origin="Hyderabad",
            destination="Bangalore",
            mode="train",
            operator="Southern Express",
            departure_time=dt(21, 0),
            arrival_time=dt(7, 0, 1),
            duration_minutes=600,
            price=1000
        ),

        # ==================================================
        # MUMBAI → PUNE
        # ==================================================

        TravelLeg(
            origin="Mumbai",
            destination="Pune",
            mode="train",
            operator="Deccan Queen",
            departure_time=dt(18, 0),
            arrival_time=dt(21, 0),
            duration_minutes=180,
            price=600
        ),

        TravelLeg(
            origin="Mumbai",
            destination="Pune",
            mode="bus",
            operator="Maharashtra Roadways",
            departure_time=dt(19, 0),
            arrival_time=dt(23, 0),
            duration_minutes=240,
            price=500
        ),

        TravelLeg(
            origin="Mumbai",
            destination="Pune",
            mode="flight",
            operator="Regional Airlines",
            departure_time=dt(20, 0),
            arrival_time=dt(21, 0),
            duration_minutes=60,
            price=2500
        ),

        # ==================================================
        # PUNE → BANGALORE
        # ==================================================

        TravelLeg(
            origin="Pune",
            destination="Bangalore",
            mode="flight",
            operator="South Airlines",
            departure_time=dt(22, 30),
            arrival_time=dt(0, 0, 1),
            duration_minutes=90,
            price=3000
        ),

        TravelLeg(
            origin="Pune",
            destination="Bangalore",
            mode="train",
            operator="Southern Express",
            departure_time=dt(20, 0),
            arrival_time=dt(10, 0, 1),
            duration_minutes=840,
            price=1400
        ),
    ]
    for leg in legs:
        leg.availability = AvailabilityStatus.AVAILABLE
        leg.last_updated = datetime.now()

    return legs

class DummyTravelDataProvider(TravelDataProvider):

    priority = 100
    name = "dummy_provider"
    def get_travel_legs(
        self,
        travel_date=None,
        mode=None,
    ) -> list[TravelLeg]:

        legs = get_all_travel_legs(
            travel_date=travel_date
        )

        if mode is not None:
            legs = [
                leg
                for leg in legs
                if leg.mode == mode
            ]

        for leg in legs:
            leg.source = "dummy_provider"

        return legs