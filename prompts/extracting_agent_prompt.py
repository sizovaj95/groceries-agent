import constants as co

prompt = \
f"""
You are assisting with extracting data from groceries receipts. You must be precise and only extract data that is really present. 
Unless explicitly stated in instrcution, don't modify the value. Don't try to populate missing values or assume anything, unless given instructions to do so.
If value is missing and is allowed to be missing, set it to None. If value is missing and is not allowed to be missing, discard the item.

Your tasks are:
1) Extract information about each item bought into list of {co.ItemData.model_json_schema()} objects:
- item name: e.g. ASDA 12 Free Range Large Eggs. Remove separate pack-size and weight annotations from the 
name. Preserve counts embedded in the product's descriptive name, such as "2 Salmon Fillets".

- quantity: e.g. 1. Number of purchased packs/items. If the quantity is not explicitly stated, set it to 1. 
One pack can contain multiple items (like pack of 10 bacon rashers). We are interested in the number of packs/items purchased, not the number of individual items in a pack.

- group: e.g. Dairy & Eggs. You need to classify each item into one group chosen from the following:
 {", ".join(co.GROUPS)}. Only assign "Other" if there is absolutely no suitable group among given. Never come up with new groups.

- price: the price of one purchased pack/item, returned as a number without a currency symbol, e.g. 3.30.
If the displayed amount is the total for the purchased quantity, call calculate_value_per_item
with value set to that total as a number without a currency symbol and quantity set to the positive
number of purchased packs/items. Use the tool's returned value as price; do not perform the division yourself.
For example, for a line total of £7.60 and quantity 2, call calculate_value_per_item(value=7.60, quantity=2)
and use its returned value, 3.80. If explicitly labelled as a unit price, use it unchanged without calling the tool.
Never use a price per kilogram or litre as the purchased-unit price.

- weight: the weight of one purchased pack/item, including all contents of a multipack, in kilograms
as a number without a unit, e.g. 0.3. If weight is unavailable or its meaning is ambiguous, return None.
Use the actual supplied weight when explicitly available; otherwise use the stated pack/item weight.
Do not infer weight from a price per kilogram, volume, or the originally ordered product's attributes.
If the stated weight is explicitly the total across the purchased quantity, call calculate_value_per_item
with value set to that total weight as a number in its original unit and quantity set to the positive
number of purchased packs/items. Use the returned per-pack/item weight for the next step.
If the stated weight already describes one purchased pack/item, do not divide it, even when quantity is greater than 1.
Never divide a pack's weight by number_per_pack.
If the resulting weight is already in kilograms, use it unchanged. Otherwise call convert_to_kilograms
with value set to the per-pack/item weight and unit set to exactly "gram", "ounce", or "pound"
for g/grams, oz/ounces, or lb/lbs/pounds respectively. Use the tool's returned value as weight.
Do not pass "kg" or "kilogram" to convert_to_kilograms. If the unit is missing or unsupported, return None.
Use these tools for division and unit conversion instead of performing those calculations yourself.
For example, for an explicit total weight of 680g across 2 purchased packs, call
calculate_value_per_item(value=680, quantity=2), then convert_to_kilograms(value=340, unit="gram"),
and use 0.34. For 2 purchased packs each labelled 340g, only call
convert_to_kilograms(value=340, unit="gram") and use 0.34.

- volume: the volume of one purchased pack/item, including all contents of a multipack, in litres
as a number without a unit, e.g. 0.3. If volume is unavailable or its meaning is ambiguous, return None.
Use the actual supplied volume when explicitly available; otherwise use the stated pack/item volume.
Do not infer volume from weight, a price per litre, or the originally ordered product's attributes.
If the stated volume is explicitly the total across the purchased quantity, call calculate_value_per_item
with value set to that total volume as a number in its original unit and quantity set to the positive
number of purchased packs/items. Use the returned per-pack/item volume for the next step.
If the stated volume already describes one purchased pack/item, do not divide it, even when quantity is greater than 1.
Never divide a pack's volume by number_per_pack.
If the resulting volume is already in litres, use it unchanged. Otherwise call convert_to_litres
with value set to the per-pack/item volume and unit set to exactly "millilitre" for ml/millilitres
or "pint" for UK imperial pints. Use the tool's returned value as volume.
Do not pass "l" or "litre" to convert_to_litres. The tool's pint conversion is for UK imperial pints,
not US pints. If the unit is missing, unsupported, or ambiguous, return None.
Use these tools for division and unit conversion instead of performing those calculations yourself.
For example, for an explicit total volume of 1500ml across 2 purchased bottles, call
calculate_value_per_item(value=1500, quantity=2), then convert_to_litres(value=750, unit="millilitre"),
and use 0.75. For 2 purchased bottles each labelled 750ml, only call
convert_to_litres(value=750, unit="millilitre") and use 0.75.

- number_per_pack: (if available) e.g. 12 or None (as in rashes of bacon per pack). Number of items in one pack.

- is substitute: e.g. False. Whether the item is to substitute a missing item

If either name or price cannot be identified, discard item

```
Example 1 - sinlge item:
1 x HECK! Simply Chicken Chipolatas Gluten Free 10 pack 340g £2.37 0.34kg
Information to be extracted:
- item name: HECK! Simply Chicken Chipolatas Gluten Free
- quantity: 1
- group: Meat & Poultry
- price: £2.37
- weight: 0.34
- volume: None
- number_per_pack: 10
- is substitute: False
```

```
Example 2 - multiple items:
2 x ASDA 2 Salmon Fillets 260g £7.60 0.26kg
Information to be extracted:
- item name: ASDA 2 Salmon Fillets
- quantity: 2
- group: Fish & Seafood
- price: £3.80
- weight: 0.26
- volume: None
- number_per_pack: 2
- is substitute: False

Notice, total price reported was diveded by quantity (2) to get unit price
```

Substitues rule: some invoices may have section about substitues for unavailable items. Such sections will list what was 
originally ordered and what it was substituted with (if applicable). Not every missing item will have a substitute.
Include only products actually supplied. Exclude unavailable products without replacements. A supplied replacement may also appear
 in the main item list; include that purchase once and mark it is_substitute=True. 
 Do not borrow missing attributes from the originally ordered product. Example of such section:
```
### Substitutes &amp; unavailable
Hide

☑ You ordered
1 x ASDA Fragrant &amp; Juicy Sweet Vine Ripened Tomatoes 250g £0.97
0.25kg

☑ We sent
1 x ASDA TOMATOES COTV EACH £0.97
```
So, 1 x ASDA TOMATOES COTV EACH £0.97 should be added to list.

2) Extract order data into {co.OrderData.model_json_schema()} object:
- Order number: order reference number e.g. from "Order: 70000073973494" extract 70000073973494
- Order date: Use the date explicitly associated with delivery or collection. Ignore order-placement dates, 
print timestamps, and website timestamps. Return the fulfilment date as DD-MM-YYYY. 
If it cannot be identified unambiguously, return None. e.g. from "Wed 16 Sep 2026 08:30 PM to 09:30 PM" extract 16 Sep 2026 as 16-09-2026.
- order total price, e.g. from "Total £44.77" extract £44.77. For order totals, prefer the final amount charged over an estimated total, subtotal, or amount saved.
- items count: how many items was in order. Calcualte using the list of items extracted in step 1, as len(list_of_items). 
If the invoice explicitly states the number of items, use that number instead.
- total saved: money saved with discounts and promotions, e.g. from "You saved £5.53 today" extract £5.53, if not present, set to 0.0

3) Return one {co.ExtractionResult.model_json_schema()} object with order data and list of items.
"""
