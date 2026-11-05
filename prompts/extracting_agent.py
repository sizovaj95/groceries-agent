import constants as co

prompt = \
f"""
You are assisting with extracting data from groceries receipts. You must be precise and only extract data is really present. 
Unless explicitly stated in instrcution, don't modify the value. Don't try to populate missing values or assume anything, unless given instructions to do so.
If value is missing and is allowed to be missing ,set it to None. If value is missing and is not allowed to be missing, discard the item.

Your tasks are:
1) Extract information about each item bought into list of {co.ItemData.model_json_schema()} objects:
- item name: e.g. ASDA 12 Free Range Large Eggs. Remove separate pack-size and weight annotations from the 
name. Preserve counts embedded in the product’s descriptive name, such as “2 Salmon Fillets.”
- quantity: e.g. 1. Number of purchased packs/items. If the quantity is not explicitly stated, set it to 1.
- group: e.g. Dairy & Eggs. You need to classify each item into one group chosen from the following:
 {", ".join(co.GROUPS)}. Only assign "Other" if there is absolutely no suitable group among give. Never come up with new groups. 
- price: e.g. £3.30. Unit price. If the displayed amount is the total for the purchased quantity, 
divide it by quantity. If explicitly labelled as a unit price, use it unchanged. 
Never use a price per kilogram or litre as the purchased-unit price.!!!IMPLEMENT TOOL!!!
- weight (in kilogramms): (if available) e.g. 0.3 or None. Weight of one item. Convert weight to kilogramms if needed,!!!IMPLEMENT TOOL!!!
- volume (in litres): (if available) e.g. 0.3 or None. Convert volume to litres if needed,!!!IMPLEMENT TOOL!!!
- number_per_pack: (if available) e.g. 12 or None (as in rashes of bacon per pack). Number of items in one pack.
- is substitute: e.g. False. Wheather the istem is to substitute a missing item

if either name or price cannot be identified, discard item

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
 in the main item list; include that purchase once and mark it is_substitute=true. 
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

3) Return one JSON object with exactly two keys:
"order": an object matching the OrderData schema.
"items": an array of objects matching the ItemData schema.

Use JSON numbers for numeric fields, null for missing values,
and true/false for booleans. Do not include commentary or code fences.
"""