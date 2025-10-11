"""Helper utility functions."""

import math
import re
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Tuple, Union

import pandas as pd


def validate_coordinates(latitude: float, longitude: float) -> bool:
    """Validate geographic coordinates.

    Args:
        latitude: Latitude in decimal degrees
        longitude: Longitude in decimal degrees

    Returns:
        True if coordinates are valid, False otherwise
    """
    try:
        lat = float(latitude)
        lon = float(longitude)
        return (-90 <= lat <= 90) and (-180 <= lon <= 180)
    except (ValueError, TypeError):
        return False


def validate_icao_code(icao_code: str) -> bool:
    """Validate ICAO airport code format.

    Args:
        icao_code: ICAO code to validate

    Returns:
        True if valid ICAO code format, False otherwise
    """
    # ICAO codes are 4 letters
    return bool(re.match(r"^[A-Z]{4}$", icao_code.upper().strip()))


def validate_iata_code(iata_code: str) -> bool:
    """Validate IATA airport code format.

    Args:
        iata_code: IATA code to validate

    Returns:
        True if valid IATA code format, False otherwise
    """
    # IATA codes are 3 letters
    return bool(re.match(r"^[A-Z]{3}$", iata_code.upper().strip()))


def format_timestamp(
    timestamp: Union[datetime, pd.Timestamp, str],
    format_string: str = "%Y-%m-%d %H:%M:%S UTC",
) -> str:
    """Format timestamp for display.

    Args:
        timestamp: Timestamp to format
        format_string: Format string for strftime

    Returns:
        Formatted timestamp string
    """
    if isinstance(timestamp, str):
        # Try to parse string timestamp
        try:
            timestamp = pd.to_datetime(timestamp)
        except (ValueError, TypeError):
            return str(timestamp)  # Return as-is if parsing fails

    if isinstance(timestamp, pd.Timestamp):
        timestamp = timestamp.to_pydatetime()

    if isinstance(timestamp, datetime):
        # Ensure timezone info
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        return timestamp.strftime(format_string)


def _parse_relative_time_range(
    time_range: str,
) -> Tuple[Optional[datetime], Optional[datetime]]:
    """Parse relative time range like 'last 24 hours' or 'next 6 days'."""
    now = datetime.now()  # Use timezone-naive datetime to match existing CLI behavior

    number_match = re.search(r"(\d+)", time_range)
    if not number_match:
        return None, None

    number = int(number_match.group(1))
    is_last = "last" in time_range

    # Determine time unit and calculate delta
    if "hour" in time_range:
        delta = timedelta(hours=number)
    elif "day" in time_range:
        delta = timedelta(days=number)
    elif "week" in time_range:
        delta = timedelta(weeks=number)
    else:
        return None, None

    # Calculate start and end times
    if is_last:
        return now - delta, now

    return now, now + delta


def _parse_absolute_time_range(
    time_range: str,
) -> Tuple[Optional[datetime], Optional[datetime]]:
    """Parse absolute time range like '2023-01-01 to 2023-01-02' or single date."""
    if " to " in time_range:
        parts = time_range.split(" to ")
        if len(parts) == 2:
            try:
                start_time = pd.to_datetime(parts[0].strip()).to_pydatetime()
                end_time = pd.to_datetime(parts[1].strip()).to_pydatetime()
                return start_time, end_time
            except (ValueError, TypeError):
                pass
    else:
        # Try to parse as single date
        try:
            single_date = pd.to_datetime(time_range).to_pydatetime()
            return single_date, single_date
        except (ValueError, TypeError):
            pass

    return None, None


def parse_time_range(time_range: str) -> Tuple[Optional[datetime], Optional[datetime]]:
    """Parse time range string into start and end datetimes.

    Args:
        time_range: Time range string (e.g., "2023-01-01 to 2023-01-02", "last 24 hours", "next 6 hours")

    Returns:
        Tuple of (start_time, end_time)
    """
    time_range = time_range.strip().lower()

    # Handle relative time ranges
    if "last" in time_range or "next" in time_range:
        return _parse_relative_time_range(time_range)

    # Handle explicit date ranges and single dates
    return _parse_absolute_time_range(time_range)


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great circle distance between two points on Earth.

    Args:
        lat1: Latitude of first point in decimal degrees
        lon1: Longitude of first point in decimal degrees
        lat2: Latitude of second point in decimal degrees
        lon2: Longitude of second point in decimal degrees

    Returns:
        Distance in kilometers
    """
    # Convert to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))

    # Earth's radius in kilometers
    R = 6371

    return R * c


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string
    """
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math

    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)

    return f"{s} {size_names[i]}"


def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert value to float.

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        Float value or default
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert value to integer.

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        Integer value or default
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def truncate_string(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """Truncate string to maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix


def clean_filename(filename: str) -> str:
    """Clean filename by removing invalid characters.

    Args:
        filename: Original filename

    Returns:
        Cleaned filename
    """
    # Remove invalid characters for most filesystems
    invalid_chars = r'<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, "_")

    # Remove leading/trailing spaces and dots
    filename = filename.strip(" .")

    # Ensure not empty
    if not filename:
        filename = "unnamed"

    return filename


def merge_dicts(*dicts: dict) -> dict:
    """Merge multiple dictionaries, with later ones taking precedence.

    Args:
        *dicts: Dictionaries to merge

    Returns:
        Merged dictionary
    """
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result


def chunk_list(lst: list, chunk_size: int) -> list:
    """Split list into chunks of specified size.

    Args:
        lst: List to chunk
        chunk_size: Size of each chunk

    Returns:
        List of chunks
    """
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]
