from typing import Dict


def cart_count(request) -> Dict[str, int]:
    cart = request.session.get("cart", {})
    if not isinstance(cart, dict):
        cart = {}
    return {"cart_count": sum(cart.values())}

