from math import pi, sqrt


EARTH_RADIUS_KM = 6371
EARTH_MU = 398600
SIDEREAL_DAY_SECONDS = 86164.09


def orbital_period(height_km: float) -> float:
    """Вернуть период круговой орбиты в секундах по высоте в км."""
    return 2 * pi * sqrt((EARTH_RADIUS_KM + height_km) ** 3 / EARTH_MU)


def orbital_speed(height_km: float) -> float:
    """Вернуть оценку орбитальной скорости в км/с по высоте в км."""
    return sqrt(EARTH_MU / (EARTH_RADIUS_KM + height_km))


def time_seconds(clock: str) -> int:
    """Перевести время ЧЧ:ММ:СС в число секунд от начала суток."""
    hours, minutes, seconds = map(int, clock.split(":"))
    return hours * 3600 + minutes * 60 + seconds


def main() -> None:
    """Проверить расчёты по сохранённому прогнозу на 08.10.2026."""
    # время местное, utc+5; все интервалы находятся внутри одних суток
    satellites = [
        (
            "МКС", 416, 425, 15.48757000,
            [
                ("10:13:46", "10:19:24"),
                ("11:49:40", "11:56:30"),
                ("13:26:32", "13:33:22"),
                ("15:03:24", "15:09:58"),
                ("16:41:30", "16:44:18"),
            ],
        ),
        (
            "Iridium 106", 776, 779, 14.34218681,
            [
                ("03:01:15", "03:11:29"),
                ("04:43:17", "04:51:42"),
                ("13:26:04", "13:33:58"),
                ("15:06:05", "15:16:25"),
                ("16:49:50", "16:52:01"),
            ],
        ),
    ]

    for name, perigee, apogee, revolutions, passes in satellites:
        height = (perigee + apogee) / 2
        period = orbital_period(height)
        service_period = 1440 / revolutions
        difference = (period / 60 - service_period) / service_period * 100
        print(f"{name}: h = {height:.1f} км; v = {orbital_speed(height):.4f} км/с")
        print(f"T = {period / 60:.4f} мин; T по n = {service_period:.4f} мин")
        print(f"Расхождение = {difference:.4f}%")
        print(f"Поворот Земли за виток = {360 * period / SIDEREAL_DAY_SECONDS:.2f}°")

        total_seconds = 0
        for start, end in passes:
            duration = time_seconds(end) - time_seconds(start)
            total_seconds += duration
            print(f"{start} - {end}: {duration // 60} мин {duration % 60} с")

        print(f"Пролётов за сутки: {len(passes)}")
        print(f"Сумма: {total_seconds // 60} мин {total_seconds % 60} с")
        print(f"Доля суток: {total_seconds / 86400 * 100:.2f}%")
        print()


if __name__ == "__main__":
    main()
