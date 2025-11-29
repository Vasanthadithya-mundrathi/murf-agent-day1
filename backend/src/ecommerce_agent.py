"""
Day 9: E-commerce Voice Agent (ACP-Inspired)
TechStyle Store - Developer merchandise shopping assistant
"""

import json
import uuid
from datetime import datetime
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from livekit.agents import Agent, AgentSession, RunContext, function_tool, RoomInputOptions
from livekit.agents.llm import ChatContext
from livekit.plugins import deepgram, openai, murf

# Paths
CATALOG_PATH = Path(__file__).parent.parent / "shared-data" / "product_catalog.json"
ORDERS_PATH = Path(__file__).parent.parent / "shared-data" / "ecommerce_orders.json"


@dataclass
class CartItem:
    """Line item in cart (ACP-style)"""
    product_id: str
    product_name: str
    quantity: int
    unit_amount: int  # Price per unit
    currency: str
    size: Optional[str] = None
    color: Optional[str] = None


@dataclass
class ShoppingSession:
    """Session state for shopping"""
    catalog: dict = field(default_factory=dict)
    cart: list[CartItem] = field(default_factory=list)
    last_shown_products: list[dict] = field(default_factory=list)  # Track what was just shown
    buyer_name: str = ""
    buyer_email: str = ""
    last_order_id: str = ""


def load_catalog() -> dict:
    """Load product catalog from JSON"""
    if CATALOG_PATH.exists():
        with open(CATALOG_PATH, "r") as f:
            return json.load(f)
    return {"products": [], "store_info": {}}


def load_orders() -> list:
    """Load existing orders"""
    if ORDERS_PATH.exists():
        with open(ORDERS_PATH, "r") as f:
            return json.load(f)
    return []


def save_orders(orders: list):
    """Save orders to JSON (ACP-style persistence)"""
    ORDERS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(ORDERS_PATH, "w") as f:
        json.dump(orders, f, indent=2)


# ============== ACP-INSPIRED COMMERCE LAYER ==============

def filter_products(products: list, 
                   category: str = None,
                   max_price: int = None,
                   min_price: int = None,
                   color: str = None,
                   search_term: str = None) -> list:
    """Filter products based on criteria"""
    results = products.copy()
    
    if category:
        results = [p for p in results if category.lower() in p.get("category", "").lower()]
    
    if max_price:
        results = [p for p in results if p.get("price", 0) <= max_price]
    
    if min_price:
        results = [p for p in results if p.get("price", 0) >= min_price]
    
    if color:
        results = [p for p in results if color.lower() in p.get("color", "").lower()]
    
    if search_term:
        search_lower = search_term.lower()
        results = [p for p in results if 
                  search_lower in p.get("name", "").lower() or 
                  search_lower in p.get("description", "").lower() or
                  search_lower in p.get("category", "").lower()]
    
    return results


def find_product_by_id(products: list, product_id: str) -> dict | None:
    """Find a specific product by ID"""
    for p in products:
        if p["id"] == product_id:
            return p
    return None


def find_product_by_name(products: list, name: str) -> dict | None:
    """Find a product by name (fuzzy match)"""
    name_lower = name.lower()
    for p in products:
        if name_lower in p.get("name", "").lower():
            return p
    return None


# ============== FUNCTION TOOLS ==============

@function_tool
def browse_catalog(ctx: RunContext[ShoppingSession], 
                  category: str = "",
                  max_price: int = 0,
                  color: str = "",
                  search: str = "") -> str:
    """
    Browse products in the catalog with optional filters.
    
    Args:
        category: Filter by category (mugs, tshirts, hoodies, stickers, caps, accessories)
        max_price: Maximum price filter in INR
        color: Filter by color (black, white, blue, gray, etc.)
        search: Search term for product name or description
    """
    catalog = ctx.userdata.catalog
    products = catalog.get("products", [])
    
    # Apply filters
    results = filter_products(
        products,
        category=category if category else None,
        max_price=max_price if max_price > 0 else None,
        color=color if color else None,
        search_term=search if search else None
    )
    
    if not results:
        return "No products found matching your criteria. Try a different search or browse all categories."
    
    # Store for reference
    ctx.userdata.last_shown_products = results[:5]
    
    # Format response
    lines = [f"Found {len(results)} products:"]
    for i, p in enumerate(results[:5], 1):
        sizes = f" (Sizes: {', '.join(p.get('sizes', []))})" if 'sizes' in p else ""
        color_info = f", {p.get('color', '')}" if p.get('color') else ""
        lines.append(f"{i}. {p['name']} - ₹{p['price']}{color_info}{sizes}")
    
    if len(results) > 5:
        lines.append(f"...and {len(results) - 5} more. Ask me to narrow down if needed!")
    
    return "\n".join(lines)


@function_tool
def get_product_details(ctx: RunContext[ShoppingSession], product_name: str) -> str:
    """
    Get detailed information about a specific product.
    
    Args:
        product_name: Name or partial name of the product
    """
    catalog = ctx.userdata.catalog
    products = catalog.get("products", [])
    
    product = find_product_by_name(products, product_name)
    
    if not product:
        return f"Couldn't find a product matching '{product_name}'. Try browsing the catalog first."
    
    details = [
        f"📦 {product['name']}",
        f"💰 Price: ₹{product['price']}",
        f"📝 {product['description']}"
    ]
    
    if product.get('color'):
        details.append(f"🎨 Color: {product['color']}")
    
    if product.get('sizes'):
        details.append(f"📏 Available sizes: {', '.join(product['sizes'])}")
    
    details.append(f"✅ {'In stock' if product.get('in_stock', True) else 'Out of stock'}")
    
    return "\n".join(details)


@function_tool
def add_to_cart(ctx: RunContext[ShoppingSession], 
               product_name: str, 
               quantity: int = 1,
               size: str = "") -> str:
    """
    Add a product to the shopping cart.
    
    Args:
        product_name: Name of the product OR position number (1st, 2nd, etc.) from last shown list
        quantity: Number of items to add
        size: Size for clothing items (S, M, L, XL)
    """
    catalog = ctx.userdata.catalog
    products = catalog.get("products", [])
    product = None
    
    # Check if referring to position in last shown products
    position_words = {"first": 0, "second": 1, "third": 2, "fourth": 3, "fifth": 4,
                     "1st": 0, "2nd": 1, "3rd": 2, "4th": 3, "5th": 4}
    
    for word, idx in position_words.items():
        if word in product_name.lower():
            if ctx.userdata.last_shown_products and idx < len(ctx.userdata.last_shown_products):
                product = ctx.userdata.last_shown_products[idx]
                break
    
    # If not a position reference, search by name
    if not product:
        product = find_product_by_name(products, product_name)
    
    if not product:
        return f"Couldn't find '{product_name}'. Try browsing the catalog first."
    
    # Check if size is required
    if product.get("sizes") and not size:
        return f"Please specify a size for {product['name']}. Available: {', '.join(product['sizes'])}"
    
    # Check if size is valid
    if size and product.get("sizes") and size.upper() not in product["sizes"]:
        return f"Size {size} not available. Choose from: {', '.join(product['sizes'])}"
    
    # Add to cart
    cart_item = CartItem(
        product_id=product["id"],
        product_name=product["name"],
        quantity=quantity,
        unit_amount=product["price"],
        currency=product.get("currency", "INR"),
        size=size.upper() if size else None,
        color=product.get("color")
    )
    
    # Check if already in cart
    for item in ctx.userdata.cart:
        if item.product_id == product["id"] and item.size == cart_item.size:
            item.quantity += quantity
            total_in_cart = sum(i.quantity * i.unit_amount for i in ctx.userdata.cart)
            return f"Updated {product['name']} quantity to {item.quantity}. Cart total: ₹{total_in_cart}"
    
    ctx.userdata.cart.append(cart_item)
    total_in_cart = sum(i.quantity * i.unit_amount for i in ctx.userdata.cart)
    
    size_info = f" (Size: {size.upper()})" if size else ""
    return f"Added {quantity}x {product['name']}{size_info} to cart. Cart total: ₹{total_in_cart}"


@function_tool
def view_cart(ctx: RunContext[ShoppingSession]) -> str:
    """
    View all items currently in the shopping cart.
    """
    cart = ctx.userdata.cart
    
    if not cart:
        return "Your cart is empty. Browse some products to get started!"
    
    lines = ["🛒 YOUR CART:"]
    total = 0
    
    for item in cart:
        item_total = item.quantity * item.unit_amount
        total += item_total
        size_info = f" ({item.size})" if item.size else ""
        lines.append(f"• {item.quantity}x {item.product_name}{size_info} - ₹{item_total}")
    
    lines.append(f"\n💰 TOTAL: ₹{total}")
    
    return "\n".join(lines)


@function_tool
def remove_from_cart(ctx: RunContext[ShoppingSession], product_name: str) -> str:
    """
    Remove a product from the cart.
    
    Args:
        product_name: Name of the product to remove
    """
    cart = ctx.userdata.cart
    name_lower = product_name.lower()
    
    for i, item in enumerate(cart):
        if name_lower in item.product_name.lower():
            removed = cart.pop(i)
            return f"Removed {removed.product_name} from cart."
    
    return f"'{product_name}' is not in your cart."


@function_tool
def update_cart_quantity(ctx: RunContext[ShoppingSession], product_name: str, new_quantity: int) -> str:
    """
    Update the quantity of an item in the cart.
    
    Args:
        product_name: Name of the product
        new_quantity: New quantity (0 to remove)
    """
    cart = ctx.userdata.cart
    name_lower = product_name.lower()
    
    for i, item in enumerate(cart):
        if name_lower in item.product_name.lower():
            if new_quantity <= 0:
                removed = cart.pop(i)
                return f"Removed {removed.product_name} from cart."
            else:
                item.quantity = new_quantity
                return f"Updated {item.product_name} to quantity {new_quantity}."
    
    return f"'{product_name}' is not in your cart."


@function_tool
def set_buyer_info(ctx: RunContext[ShoppingSession], name: str, email: str = "") -> str:
    """
    Set buyer information for the order.
    
    Args:
        name: Buyer's name
        email: Buyer's email (optional)
    """
    ctx.userdata.buyer_name = name
    ctx.userdata.buyer_email = email
    
    return f"Got it, {name}! Ready to place your order."


@function_tool
def place_order(ctx: RunContext[ShoppingSession]) -> str:
    """
    Place the order with items in the cart (ACP-style order creation).
    Creates a structured order object and persists it.
    """
    cart = ctx.userdata.cart
    
    if not cart:
        return "Your cart is empty! Add some products before placing an order."
    
    if not ctx.userdata.buyer_name:
        return "I need your name to place the order. What's your name?"
    
    # Calculate totals
    total = sum(item.quantity * item.unit_amount for item in cart)
    
    # Create ACP-style order object
    order = {
        "id": f"ORD-{uuid.uuid4().hex[:8].upper()}",
        "status": "CONFIRMED",
        "created_at": datetime.now().isoformat(),
        "buyer": {
            "name": ctx.userdata.buyer_name,
            "email": ctx.userdata.buyer_email or None
        },
        "line_items": [
            {
                "product_id": item.product_id,
                "product_name": item.product_name,
                "quantity": item.quantity,
                "unit_amount": item.unit_amount,
                "currency": item.currency,
                "size": item.size,
                "color": item.color,
                "line_total": item.quantity * item.unit_amount
            }
            for item in cart
        ],
        "total": {
            "amount": total,
            "currency": "INR"
        },
        "item_count": sum(item.quantity for item in cart)
    }
    
    # Persist order
    orders = load_orders()
    orders.append(order)
    save_orders(orders)
    
    # Store order ID and clear cart
    ctx.userdata.last_order_id = order["id"]
    ctx.userdata.cart = []
    
    return f"""
✅ ORDER PLACED SUCCESSFULLY!

Order ID: {order['id']}
Customer: {order['buyer']['name']}
Items: {order['item_count']} items
Total: ₹{order['total']['amount']}
Status: {order['status']}

Thank you for shopping with TechStyle Store! 🎉
"""


@function_tool
def get_last_order(ctx: RunContext[ShoppingSession]) -> str:
    """
    Get details of the last placed order.
    """
    orders = load_orders()
    
    if not orders:
        return "You haven't placed any orders yet."
    
    # Get latest order
    order = orders[-1]
    
    lines = [
        f"📦 ORDER: {order['id']}",
        f"📅 Placed: {order['created_at'][:10]}",
        f"👤 Customer: {order['buyer']['name']}",
        f"📊 Status: {order['status']}",
        "\nItems:"
    ]
    
    for item in order["line_items"]:
        size_info = f" ({item['size']})" if item.get('size') else ""
        lines.append(f"  • {item['quantity']}x {item['product_name']}{size_info} - ₹{item['line_total']}")
    
    lines.append(f"\n💰 Total: ₹{order['total']['amount']}")
    
    return "\n".join(lines)


@function_tool
def get_order_history(ctx: RunContext[ShoppingSession]) -> str:
    """
    Get all previous orders.
    """
    orders = load_orders()
    
    if not orders:
        return "No order history found."
    
    lines = [f"📋 ORDER HISTORY ({len(orders)} orders):"]
    
    for order in orders[-5:]:  # Last 5 orders
        lines.append(f"• {order['id']} - {order['item_count']} items - ₹{order['total']['amount']} - {order['status']}")
    
    total_spent = sum(o['total']['amount'] for o in orders)
    lines.append(f"\n💳 Total spent: ₹{total_spent}")
    
    return "\n".join(lines)


# ============== AGENT SETUP ==============

ECOMMERCE_AGENT_INSTRUCTIONS = """You are a friendly shopping assistant for TechStyle Store - a premium developer merchandise shop!

## Your Personality
- Enthusiastic and helpful
- Knowledgeable about tech culture and developer lifestyle
- Conversational but efficient
- Use casual, friendly language

## What You Sell
- Developer coffee mugs (Python, Debug, Code themes)
- Programming t-shirts (Git, React, AI/ML designs)
- Cozy hoodies (Code Ninja, Open Source, Dark Mode)
- Laptop stickers (Developer packs, Framework packs)
- Caps (Binary code, AWS designs)
- Accessories (Mousepads, desk items)

## Your Capabilities
1. **Browse Products**: Show products by category, price range, or color
2. **Product Details**: Give detailed info about specific items
3. **Cart Management**: Add/remove items, update quantities
4. **Place Orders**: Collect buyer info and confirm orders
5. **Order History**: Show past orders and spending

## Conversation Flow
1. Greet and ask what they're looking for
2. Help them browse (by category, price, color, or free search)
3. When they find something, help add it to cart (with size if needed)
4. Confirm cart contents before checkout
5. Get their name, place the order, confirm details

## Important Rules
- Always mention prices in rupees (₹)
- For t-shirts and hoodies, always ask for size (S, M, L, XL)
- Summarize cart total after adding items
- Before placing order, confirm cart contents
- After order, provide the order ID

## Handling References
When user says "the first one" or "that hoodie", refer to the last products you showed them.

Start by greeting the customer and asking what kind of developer gear they're looking for today!"""


if __name__ == "__main__":
    from livekit.agents import WorkerOptions, cli
    from livekit.plugins import silero

    async def entrypoint(ctx: AgentSession):
        # Initialize session
        session_data = ShoppingSession()
        session_data.catalog = load_catalog()

        # Configure LLM
        llm = openai.LLM.with_ollama(
            model="mistral",
            base_url="http://127.0.0.1:11434/v1",
        )

        # Configure TTS - Friendly voice for shopping
        tts = murf.TTS(
            voice="en-US-natalie",  # Friendly American English
            model="GEN2",
            sample_rate=24000,
        )

        # Configure STT
        stt = deepgram.STT(model="nova-3", language="en")

        # Configure VAD
        vad = silero.VAD.load()

        # Build initial context
        catalog = session_data.catalog
        categories = set(p.get("category", "") for p in catalog.get("products", []))
        
        initial_ctx = ChatContext()
        initial_ctx.add_message(
            role="system",
            content=f"""{ECOMMERCE_AGENT_INSTRUCTIONS}

Available categories: {', '.join(categories)}
Total products: {len(catalog.get('products', []))}
"""
        )

        # Create agent with commerce tools
        agent = Agent(
            instructions=ECOMMERCE_AGENT_INSTRUCTIONS,
            chat_ctx=initial_ctx,
            llm=llm,
            tts=tts,
            stt=stt,
            vad=vad,
            tools=[
                browse_catalog,
                get_product_details,
                add_to_cart,
                view_cart,
                remove_from_cart,
                update_cart_quantity,
                set_buyer_info,
                place_order,
                get_last_order,
                get_order_history
            ]
        )

        # Start session
        await ctx.start(
            agent=agent,
            room_input_options=RoomInputOptions(),
            userdata=session_data
        )

    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
