"""
Format the given amount as a currency value in Vietnamese Dong (VNĐ).

Args:
    amount (float): The amount to be formatted as currency.

Returns:
    str: The formatted currency value in Vietnamese Dong (VNĐ).
"""


def format_currency(amount):
    amount_str = str(amount)

    integer_part, decimal_part = (
        amount_str.split(".") if "." in amount_str else (amount_str, "")
    )

    integer_part_formatted = ""
    while integer_part:
        integer_part_formatted = f"{integer_part[-3:]}.{integer_part_formatted}"
        integer_part = integer_part[:-3]
    integer_part_formatted = integer_part_formatted[:-1]

    return f"{integer_part_formatted} VNĐ"


"""
Format the values of the given Enum class into a string separated by pipes (|).

Args:
    enum: The Enum class containing the values to be formatted.

Returns:
    str: The formatted Enum values separated by pipes (|).
"""


def format_enum_values(enum):
    enum_values = [choice.value for choice in enum]
    return " | ".join(enum_values)
