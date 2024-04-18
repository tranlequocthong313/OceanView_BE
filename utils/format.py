def format_currency(amount):
    amount_str = str(amount)

    integer_part, decimal_part = (
        amount_str.split(".") if "." in amount_str else (amount_str, "")
    )

    integer_part_formatted = ""
    while integer_part:
        integer_part_formatted = integer_part[-3:] + "." + integer_part_formatted
        integer_part = integer_part[:-3]
    integer_part_formatted = integer_part_formatted[:-1]  # Loại bỏ dấu chấm cuối cùng

    return f"{integer_part_formatted} VNĐ"
