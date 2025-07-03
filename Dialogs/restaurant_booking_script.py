# dialogs/restaurant_booking_script.py

DIALOG_SCRIPTS = {
    "restaurant_booking": {
        "steps": [
            {
                "id": "ask_people",
                "expect": "people",
                "message": {
                    "en": "How many people are you booking for?",
                    "ru": "На сколько человек вы хотите забронировать?",
                    "fr": "Pour combien de personnes souhaitez-vous réserver?",
                    "es": "¿Para cuántas personas desea reservar?",
                    "de": "Für wie viele Personen möchten Sie reservieren?",
                    "ca": "Per a quantes persones vols fer la reserva?"
                }
            },
            {
                "id": "ask_time",
                "expect": "time",
                "message": {
                    "en": "What time would you like the reservation?",
                    "ru": "На какое время вы хотите забронировать?",
                    "fr": "À quelle heure souhaitez-vous réserver?",
                    "es": "¿A qué hora desea reservar?",
                    "de": "Um wie viel Uhr möchten Sie reservieren?",
                    "ca": "A quina hora vols fer la reserva?"
                }
            },
            {
                "id": "confirm",
                "message": {
                    "en": "Great, I've booked a table for {people} at {time}. Bon appétit!",
                    "ru": "Отлично, я забронировал столик на {people} в {time}. Приятного аппетита!",
                    "fr": "Parfait, j'ai réservé une table pour {people} à {time}. Bon appétit!",
                    "es": "Genial, he reservado una mesa para {people} a las {time}. ¡Buen provecho!",
                    "de": "Super, ich habe einen Tisch für {people} um {time} reserviert. Guten Appetit!",
                    "ca": "Genial! T'he reservat una taula per a {people} a les {time}. Bon profit!"
                }
            }
        ]
    }
}
