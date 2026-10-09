"""Order checkout.

The rules live in `src/shop/specs/checkout.md` - read it first.
Both functions below are stubs: their signature is final, the bodies are yours.
Do not change the constants: the tests rely on them.
"""

PROMO_CODES = {"WELCOME10": 10, "SUMMER15": 15, "VIP35": 35}
SUPPORTED_CITIES = ("msk", "spb")
MAX_DISCOUNT_PERCENT = 30
VAT_PERCENT = 20
SHIPPING_KOPEKS = 49_000
FREE_DELIVERY_FROM_KOPEKS = 500_000
TIER_DISCOUNTS = ((10, 5), (25, 10), (50, 15))
REQUIRED_LINE_KEYS = ("sku", "qty", "unit_price_kopecks")


def _validate_single_line(current_line: dict[str, str], idx: int) -> str | None:
    """Validate keys, formats, and structural rules for an individual order item."""
    # Spec 3, Rule 3: check presence of required layout components
    for key in REQUIRED_LINE_KEYS:
        if key not in current_line:
            return f"Line {idx} is missing a required key: {key}."

    # Spec 3, Rule 2: ensure article reference contains readable characters
    sku = current_line["sku"]
    if not sku or not sku.strip():
        return f"Line {idx} has an empty or blank sku."

    # Spec 3, Rule 4 & 5: assert integer quantity constraints
    qty_str = current_line["qty"]
    if not qty_str.isdigit() and not (qty_str.startswith("-") and qty_str[1:].isdigit()):
        return f"Line {idx} contains a non-numeric quantity value."
    if int(qty_str) <= 0:
        return f"Line {idx} quantity must be a whole number greater than zero."

    # Spec 3, Rule 6 & 7: assert integer unit price metrics
    price_str = current_line["unit_price_kopecks"]
    if not price_str.isdigit() and not (price_str.startswith("-") and price_str[1:].isdigit()):
        return f"Line {idx} contains a non-numeric unit price value."
    if int(price_str) < 0:
        return f"Line {idx} unit price cannot be negative."

    return None


def validate_order(
    lines: list[dict[str, str]],
    promo_code: str = "",
    shipping_city: str = "",
) -> str | None:
    """Return a human readable reason why the order is invalid, or None if it is fine."""
    # Spec 3, Rule 1: decline completely missing configurations
    if not lines:
        return "Order lines list cannot be empty."

    seen_skus = set()

    for idx, current_line in enumerate(lines, start=1):
        # Delegate core item data inspection to lower complexity
        line_error = _validate_single_line(current_line, idx)
        if line_error is not None:
            return line_error

        # Spec 3, Rule 8: assert uniqueness criteria across the catalog items
        sku = current_line["sku"]
        if sku in seen_skus:
            return f"Duplicate article code found: {sku}."
        seen_skus.add(sku)

    # Spec 3, Rule 9: confirm coupon matches parameters
    if promo_code and promo_code not in PROMO_CODES:
        return "The provided promotional code does not exist."

    # Spec 3, Rule 10: ensure branch logic matches location constraints
    if shipping_city and shipping_city not in SUPPORTED_CITIES:
        return "The requested delivery destination city is not supported."

    return None


def calculate_order_total(
    lines: list[dict[str, str]],
    promo_code: str = "",
    shipping_city: str = "",
) -> int | None:
    """Return the order total in kopecks, or None if the order is invalid."""
    if validate_order(lines, promo_code, shipping_city) is not None:
        return None

    subtotal = 0
    total_qty = 0
    for current_line in lines:
        qty = int(current_line["qty"])
        price = int(current_line["unit_price_kopecks"])
        subtotal += qty * price
        total_qty += qty

    tier_percent = 0
    for threshold, discount_pct in TIER_DISCOUNTS:
        if total_qty >= threshold:
            tier_percent = discount_pct

    promo_percent = PROMO_CODES.get(promo_code, 0) if promo_code else 0
    chosen_percent = max(tier_percent, promo_percent)
    final_discount_percent = min(chosen_percent, MAX_DISCOUNT_PERCENT)

    discount = (subtotal * final_discount_percent + 50) // 100
    discounted_subtotal = subtotal - discount

    shipping = 0
    if shipping_city and discounted_subtotal < FREE_DELIVERY_FROM_KOPEKS:
        shipping = SHIPPING_KOPEKS

    base = discounted_subtotal + shipping
    vat = (base * VAT_PERCENT + 50) // 100

    return base + vat
