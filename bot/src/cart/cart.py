from decimal import Decimal

from aiogram.fsm.context import FSMContext

from db.repository import Product

CART_ID = 'cart'


class Cart:
    async def init(self, storage: FSMContext, storage_key: str = CART_ID):
        self.__storage = storage
        self.__storage_key = storage_key
        data = await self.__storage.get_data()
        self.__cart = data.get(CART_ID, {})
        return self

    def add(self, product: Product, quantity: int = 1):
        product_id = str(product.id)
        if product_id in self.__cart:
            self.__cart[product_id]['quantity'] += 1
        else:
            self.__cart[product_id] = {'name': product.name, 'price': str(product.price), 'quantity': quantity}

    def decrease(self, product_id: str):
        if product_id in self.__cart:
            quantity = self.__cart[product_id]['quantity']
            if quantity <= 1:
                self.delete(product_id)
            else:
                self.__cart[product_id]['quantity'] -= 1

    def delete(self, product_id: str) -> None:
        if product_id in self.__cart:
            del self.__cart[product_id]

    def clear(self):
        self.__cart = self.__storage[self.__storage_key] = {}

    def total(self):
        full_price = 0
        for item in self.__cart.values():
            full_price += item['quantity'] * Decimal(item['price'])
        return full_price

    def get_items_id(self):
        return self.__cart.keys()

    async def save(self):
        await self.__storage.update_data(cart=self.__cart)

    def __iter__(self):
        return ((k, v) for k, v in self.__cart.items())

    def __contains__(self, value):
        return value in self.__cart

    def __len__(self):
        return len(self.__cart)

    def __getitem__(self, key):
        return self.__cart[key]

    def __bool__(self):
        return bool(self.__cart)
