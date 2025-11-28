"""
Day 7: Food & Grocery Ordering Voice Agent - ROBERT
FreshMart Express - Quick commerce grocery assistant
"""

import json
import os
from datetime import datetime
from dataclasses import dataclass, field
from pathlib import Path

from livekit.agents import Agent, AgentSession, RunContext, function_tool, RoomInputOptions
from livekit.agents.llm import ChatContext
from livekit.plugins import deepgram, openai, murf

# Paths
CATALOG_PATH = Path(__file__).parent.parent / "shared-data" / "grocery_catalog.json"
ORDERS_PATH = Path(__file__).parent.parent / "shared-data" / "orders.json"


@dataclass
class CartItem:
    """Single item in cart"""
    product_id: str
    name: str
    price: float
    quantity: int
    unit: str


@dataclass
class GroceryData:
    """Session data for grocery ordering"""
    catalog: dict = field(default_factory=dict)
    cart: list[CartItem] = field(default_factory=list)
    customer_name: str = ""
    delivery_address: str = ""
    order_placed: bool = False


def load_catalog() -> dict:
    """Load the grocery catalog from JSON"""
    if CATALOG_PATH.exists():
        with open(CATALOG_PATH, "r") as f:
            return json.load(f)
    return {"products": [], "recipes": {}, "store_info": {}}


def load_orders() -> list:
    """Load existing orders"""
    if ORDERS_PATH.exists():
        with open(ORDERS_PATH, "r") as f:
            return json.load(f)
    return []


def save_orders(orders: list):
    """Save orders to JSON"""
    ORDERS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(ORDERS_PATH, "w") as f:
        json.dump(orders, f, indent=2)


def find_product(catalog: dict, search_term: str) -> dict | None:
    """Find a product by name (fuzzy match)"""
    search_lower = search_term.lower()
    for product in catalog.get("products", []):
        if search_lower in product["name"].lower():
            return product
    return None


def get_recipe_items(catalog: dict, recipe_name: str) -> list[dict]:
    """Get all products needed for a recipe"""
    recipes = catalog.get("recipes", {})
    recipe_lower = recipe_name.lower()
    
    for name, product_ids in recipes.items():
        if recipe_lower in name.lower() or name.lower() in recipe_lower:
            items = []
            for pid in product_ids:
                for product in catalog.get("products", []):
                    if product["id"] == pid:
                        items.append(product)
                        break
            return items
    return []


# ============== FUNCTION TOOLS ==============

@function_tool
def search_catalog(ctx: RunContext[GroceryData], query: str) -> str:
    """
    Search for products in the catalog.
    
    Args:
        query: Product name or category to search for
    """
    catalog = ctx.userdata.catalog
    query_lower = query.lower()
    
    matches = []
    for product in catalog.get("products", []):
        if query_lower in product["name"].lower() or query_lower in product.get("category", "").lower():
            matches.append(f"• {product['name']} - ₹{product['price']} ({product['unit']})")
    
    if matches:
        return f"Found {len(matches)} items:\n" + "\n".join(matches[:10])
    return f"No products found matching '{query}'"


@function_tool
def add_to_cart(ctx: RunContext[GroceryData], product_name: str, quantity: int = 1) -> str:
    """
    Add a product to the shopping cart.
    
    Args:
        product_name: Name of the product to add
        quantity: Number of items to add (default 1)
    """
    catalog = ctx.userdata.catalog
    product = find_product(catalog, product_name)
    
    if not product:
        return f"Sorry, couldn't find '{product_name}' in our catalog. Try searching for it first."
    
    # Check if already in cart
    for item in ctx.userdata.cart:
        if item.product_id == product["id"]:
            item.quantity += quantity
            return f"Updated {product['name']} quantity to {item.quantity}. Cart now has {len(ctx.userdata.cart)} items."
    
    # Add new item
    cart_item = CartItem(
        product_id=product["id"],
        name=product["name"],
        price=product["price"],
        quantity=quantity,
        unit=product["unit"]
    )
    ctx.userdata.cart.append(cart_item)
    
    return f"Added {quantity}x {product['name']} (₹{product['price']} each) to cart. Cart now has {len(ctx.userdata.cart)} items."


@function_tool
def add_recipe_items(ctx: RunContext[GroceryData], recipe_name: str) -> str:
    """
    Add all ingredients for a recipe/dish to the cart.
    
    Args:
        recipe_name: Name of the dish (e.g., 'peanut butter sandwich', 'pasta', 'omelette')
    """
    catalog = ctx.userdata.catalog
    items = get_recipe_items(catalog, recipe_name)
    
    if not items:
        return f"Sorry, I don't have a recipe for '{recipe_name}'. Available recipes: {', '.join(catalog.get('recipes', {}).keys())}"
    
    added = []
    for product in items:
        # Check if already in cart
        found = False
        for cart_item in ctx.userdata.cart:
            if cart_item.product_id == product["id"]:
                cart_item.quantity += 1
                found = True
                break
        
        if not found:
            cart_item = CartItem(
                product_id=product["id"],
                name=product["name"],
                price=product["price"],
                quantity=1,
                unit=product["unit"]
            )
            ctx.userdata.cart.append(cart_item)
        
        added.append(product["name"])
    
    total = sum(item.price * item.quantity for item in ctx.userdata.cart)
    return f"Added ingredients for {recipe_name}: {', '.join(added)}. Cart total: ₹{total}"


@function_tool
def remove_from_cart(ctx: RunContext[GroceryData], product_name: str) -> str:
    """
    Remove a product from the cart.
    
    Args:
        product_name: Name of the product to remove
    """
    product_lower = product_name.lower()
    
    for i, item in enumerate(ctx.userdata.cart):
        if product_lower in item.name.lower():
            removed = ctx.userdata.cart.pop(i)
            return f"Removed {removed.name} from cart. Cart now has {len(ctx.userdata.cart)} items."
    
    return f"'{product_name}' is not in your cart."


@function_tool
def update_quantity(ctx: RunContext[GroceryData], product_name: str, new_quantity: int) -> str:
    """
    Update the quantity of a product in the cart.
    
    Args:
        product_name: Name of the product
        new_quantity: New quantity (use 0 to remove)
    """
    product_lower = product_name.lower()
    
    for i, item in enumerate(ctx.userdata.cart):
        if product_lower in item.name.lower():
            if new_quantity <= 0:
                removed = ctx.userdata.cart.pop(i)
                return f"Removed {removed.name} from cart."
            else:
                item.quantity = new_quantity
                return f"Updated {item.name} to {new_quantity} quantity."
    
    return f"'{product_name}' is not in your cart."


@function_tool
def show_cart(ctx: RunContext[GroceryData]) -> str:
    """
    Show all items currently in the cart with total.
    """
    if not ctx.userdata.cart:
        return "Your cart is empty. Would you like to add something?"
    
    lines = ["Your cart contains:"]
    subtotal = 0
    
    for item in ctx.userdata.cart:
        item_total = item.price * item.quantity
        subtotal += item_total
        lines.append(f"• {item.quantity}x {item.name} ({item.unit}) - ₹{item_total}")
    
    delivery_fee = ctx.userdata.catalog.get("store_info", {}).get("delivery_fee", 29)
    total = subtotal + delivery_fee
    
    lines.append(f"\nSubtotal: ₹{subtotal}")
    lines.append(f"Delivery fee: ₹{delivery_fee}")
    lines.append(f"Total: ₹{total}")
    
    return "\n".join(lines)


@function_tool
def set_customer_info(ctx: RunContext[GroceryData], name: str, address: str) -> str:
    """
    Set customer name and delivery address for the order.
    
    Args:
        name: Customer's name
        address: Delivery address
    """
    ctx.userdata.customer_name = name
    ctx.userdata.delivery_address = address
    return f"Got it! Delivering to {name} at {address}."


@function_tool
def place_order(ctx: RunContext[GroceryData]) -> str:
    """
    Place the final order and save to JSON file.
    Call this when the customer confirms they want to place the order.
    """
    if not ctx.userdata.cart:
        return "Your cart is empty! Please add items before placing an order."
    
    if not ctx.userdata.customer_name:
        return "I need your name before placing the order. What's your name?"
    
    if not ctx.userdata.delivery_address:
        return "I need a delivery address. Where should I deliver this?"
    
    # Calculate totals
    subtotal = sum(item.price * item.quantity for item in ctx.userdata.cart)
    delivery_fee = ctx.userdata.catalog.get("store_info", {}).get("delivery_fee", 29)
    total = subtotal + delivery_fee
    
    # Create order object
    order = {
        "order_id": f"FM-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "timestamp": datetime.now().isoformat(),
        "customer_name": ctx.userdata.customer_name,
        "delivery_address": ctx.userdata.delivery_address,
        "items": [
            {
                "product_id": item.product_id,
                "name": item.name,
                "price": item.price,
                "quantity": item.quantity,
                "unit": item.unit,
                "item_total": item.price * item.quantity
            }
            for item in ctx.userdata.cart
        ],
        "subtotal": subtotal,
        "delivery_fee": delivery_fee,
        "total": total,
        "status": "received",
        "status_history": [
            {"status": "received", "timestamp": datetime.now().isoformat()}
        ]
    }
    
    # Save to orders file
    orders = load_orders()
    orders.append(order)
    save_orders(orders)
    
    ctx.userdata.order_placed = True
    
    return f"""
Order placed successfully!

Order ID: {order['order_id']}
Customer: {order['customer_name']}
Delivery to: {order['delivery_address']}
Items: {len(order['items'])} items
Total: ₹{total}

Your order will arrive in approximately 30 minutes!
Thank you for shopping with FreshMart Express!
"""


@function_tool
def check_order_status(ctx: RunContext[GroceryData], order_id: str = "") -> str:
    """
    Check the status of an order.
    
    Args:
        order_id: Optional order ID. If not provided, checks the latest order.
    """
    orders = load_orders()
    
    if not orders:
        return "No orders found in the system."
    
    if order_id:
        for order in orders:
            if order["order_id"] == order_id:
                return f"Order {order_id}: Status is '{order['status']}'. Placed on {order['timestamp'][:10]}. Total: ₹{order['total']}"
        return f"Order {order_id} not found."
    
    # Return latest order
    latest = orders[-1]
    return f"Your latest order {latest['order_id']}: Status is '{latest['status']}'. {len(latest['items'])} items, Total: ₹{latest['total']}"


@function_tool
def get_previous_orders(ctx: RunContext[GroceryData]) -> str:
    """
    Get the customer's previous orders.
    """
    orders = load_orders()
    
    if not orders:
        return "You haven't placed any orders yet."
    
    lines = [f"Found {len(orders)} previous orders:"]
    for order in orders[-5:]:  # Last 5 orders
        lines.append(f"• {order['order_id']} - {len(order['items'])} items - ₹{order['total']} - {order['status']}")
    
    return "\n".join(lines)


# ============== AGENT SETUP ==============

ROBERT_INSTRUCTIONS = """You are ROBERT, a friendly and efficient grocery shopping assistant for FreshMart Express - a quick commerce platform delivering groceries in 30 minutes!

## Your Personality
- Warm, helpful, and conversational
- Speak naturally like a helpful store assistant
- Use Indian English naturally (say "rupees" for prices)
- Be concise but friendly

## Your Capabilities
You can help customers:
1. Search for products in the catalog
2. Add items to their cart (single items or quantities)
3. Add ingredients for recipes (e.g., "I need ingredients for pasta")
4. Remove items or update quantities
5. Show cart contents and total
6. Place orders with delivery details
7. Check order status and history

## Available Recipes
You know how to bundle items for: peanut butter sandwich, cheese sandwich, pasta, omelette, aloo paratha, poha, fruit salad, breakfast basics, maggi, chai

## Conversation Flow
1. Greet the customer warmly
2. Ask what they're looking for today
3. Help them find and add items
4. Handle "ingredients for X" requests by adding all needed items
5. Confirm cart changes verbally
6. When they're done, collect name and address
7. Confirm the order and place it

## Important Rules
- Always confirm what you've added to the cart
- Mention prices in rupees (₹)
- If an item isn't found, suggest searching or alternatives
- Before placing order, always show the final cart summary
- Be helpful if they want to modify quantities or remove items

## Starting the Conversation
Greet the customer and ask what they'd like to order today. Mention you can help with individual items or complete meal ingredients."""


async def create_grocery_agent(ctx: RunContext[GroceryData]) -> Agent:
    """Create the ROBERT grocery agent"""
    
    # Load catalog into session data
    ctx.userdata.catalog = load_catalog()
    
    # Build initial context with catalog summary
    catalog = ctx.userdata.catalog
    categories = catalog.get("categories", [])
    store_name = catalog.get("store_info", {}).get("name", "FreshMart Express")
    
    initial_ctx = ChatContext()
    initial_ctx.add_message(
        role="system",
        content=f"{ROBERT_INSTRUCTIONS}\n\nStore: {store_name}\nCategories available: {', '.join(categories)}"
    )
    
    return Agent(
        instructions=ROBERT_INSTRUCTIONS,
        chat_ctx=initial_ctx,
        tools=[
            search_catalog,
            add_to_cart,
            add_recipe_items,
            remove_from_cart,
            update_quantity,
            show_cart,
            set_customer_info,
            place_order,
            check_order_status,
            get_previous_orders
        ]
    )


async def run_grocery_agent(ctx: RunContext[GroceryData]):
    """Main entry point for the grocery agent"""
    
    # Create agent
    agent = await create_grocery_agent(ctx)
    
    # Start the agent session
    await ctx.session.start(
        agent=agent,
        room_input_options=RoomInputOptions()
    )


if __name__ == "__main__":
    from livekit.agents import WorkerOptions, cli
    from livekit.plugins import silero
    
    async def entrypoint(ctx: AgentSession):
        # Initialize session data
        grocery_data = GroceryData()
        
        # Configure LLM
        llm = openai.LLM.with_ollama(
            model="mistral",
            base_url="http://127.0.0.1:11434/v1",
        )
        
        # Configure TTS (Murf AI - Ken for professional male voice)
        tts = murf.TTS(
            voice="en-IN-aarav",  # Indian English male voice
            model="GEN2",
            sample_rate=24000,
        )
        
        # Configure STT
        stt = deepgram.STT(model="nova-3", language="en-IN")
        
        # Configure VAD
        vad = silero.VAD.load()
        
        # Load catalog
        grocery_data.catalog = load_catalog()
        
        # Build initial context
        catalog = grocery_data.catalog
        categories = catalog.get("categories", [])
        recipes = list(catalog.get("recipes", {}).keys())
        
        initial_ctx = ChatContext()
        initial_ctx.add_message(
            role="system",
            content=f"""{ROBERT_INSTRUCTIONS}

Available categories: {', '.join(categories)}
Available recipes: {', '.join(recipes)}
"""
        )
        
        # Create agent with tools
        agent = Agent(
            instructions=ROBERT_INSTRUCTIONS,
            chat_ctx=initial_ctx,
            llm=llm,
            tts=tts,
            stt=stt,
            vad=vad,
            tools=[
                search_catalog,
                add_to_cart,
                add_recipe_items,
                remove_from_cart,
                update_quantity,
                show_cart,
                set_customer_info,
                place_order,
                check_order_status,
                get_previous_orders
            ]
        )
        
        # Start session with userdata
        await ctx.start(
            agent=agent,
            room_input_options=RoomInputOptions(),
            userdata=grocery_data
        )
    
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
