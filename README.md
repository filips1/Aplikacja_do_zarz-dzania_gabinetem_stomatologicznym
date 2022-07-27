# Aplikacja do zarządzania gabinetem stomatologicznym

Celem aplikacji było zaprojektowanie oraz implementacja aplikacji internetowej służącej do zarządzania gabinetem stomatologicznym. 

Do programu została napisana duża ilość testów jednostkowych i integracyjnych a także kilka testów akceptacyjnych.

Program został wykonany przy pomocy frameworka Django wraz z Celery i Django Channels a także Javascript/JQuery i AJAX. Do wykonania projektu wykorzystana została baza danych MySQL.

#Funkcjonalności
Użytkownik korzystający z systemu powinien być w stanie korzystać z poszczególnych funkcjonalności projektu bez żadnych problemów. Poniżej została utworzona lista wymagań funkcjonalnych, które program s powinien spełniać:
- Rejestracja - możliwość zarejestrowania się jako jeden z trzech aktorów: dentysta, recepcjonista, pacjent.
- Tworzenie Wizyty - dentysta lub recepcjonista mają możliwość tworzenia wizyt
- Tworzenie pacjentów - możliwy jest wgląd do zębów pacjenta. Zęby powinny być wyświetlane w postaci graficznej, gdyż wtedy najbardziej rzuca się ona w oczy
- Wyszukiwarka dentystów - pacjent powinien mieć możliwość wyszukiwania dentystów za pomocą mapy lub też wyszukiwarki
- Zarządzanie zębami - Program powinien pozwalać dentystom na dodawanie opisanych uszkodzeń zęba a także na wprowadzenie sposobu leczenia danego uszkodzenia
- Historia leczenia
- Aktualizowanie danych - Status wizyty będzie cyklicznie aktualizowany w tle przy wykorzystaniu Celery które umożliwia wykonywanie zadań w tle
- Czat - dentysta ma możliwosć komunikowania się z pacjentem za pomocą czatu utworzonego przy wykorzystaniu Django Channels umożliwiającą wykorzystanie technologii WebSocket
- Zarządzanie Gabinetem Dentystycznym - Do danego gabinetu dentystycznego mogą być przypisani dentyści i recepcjoniści

