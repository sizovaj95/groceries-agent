from langsmith import Client, evaluate

from extracting_agent import get_agent
import constants as co


agent = get_agent()


def target(inputs: dict) -> dict:
    result = agent.invoke({
            "messages": [{
                "role": "user",
                "content": f"Extract from this receipts:\n\n{inputs['markdown']}"
            }]
        })
    structured_response = result["structured_response"]
    output = {
        "order": structured_response.order,
        "items": structured_response.items
    }
    return output


def evaluate_orders(outputs: dict, reference_outputs: dict) -> dict:
    expected_order = reference_outputs['order']
    result_order = outputs['order']
    if isinstance(expected_order, co.OrderData):
        expected_order = expected_order.as_dict()
    if isinstance(result_order, co.OrderData):
        result_order = result_order.as_dict()
    all_keys = list(expected_order.keys())
    comment = ''
    num_mismatch = 0
    for key in all_keys:
        expected = expected_order.get(key)
        result = result_order.get(key)
        if expected != result:
            num_mismatch += 1
            comment += f"Mismatch in {key}: expected `{expected}` | result `{result}`\n"
    score_dict = {
        "key": "exact match",
        "score": round((len(all_keys) - num_mismatch) / len(all_keys), 2),
        "comment": comment
    }
    return score_dict


# def evaluate(outputs: dict, reference_outputs: dict) -> dict:
#     expected_order = reference_outputs['order']
#     expected_items = reference_outputs['items']

#     result_order = outputs['order']
#     redsult_items = outputs['items']


def main():
    result = evaluate(
        target, data="Receipts Extraction Results",
        evaluators=[evaluate_orders]
    )
    print(result)


if __name__ == "__main__":
    main()
