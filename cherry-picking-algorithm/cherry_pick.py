def cherry_pick(alerts: list, num_of_results: int = 4) -> list:

    # If num_of_results are greater than list size, then no need to filter just return full list
    if len(alerts) <= num_of_results:
        return [alert["_id"] for alert in alerts]

    # Set the first num_of_results elements as first highest priority and maintain worst_priority
    prioritised = []
    worst_priority = 1
    for index in range(num_of_results):
        if not validate_alert(alerts[index]):
            continue
        prioritised.append(alerts[index])
        priority = convert_alert_to_priority(
            alerts[index]["Details"]["Type"], alerts[index]["Details"]["SubType"]
        )
        worst_priority = priority if priority > worst_priority else worst_priority

    # Iterate over the remaining alerts
    for index in range(num_of_results, len(alerts)):
        if not validate_alert(alerts[index]):
            continue
        priority = convert_alert_to_priority(
            alerts[index]["Details"]["Type"], alerts[index]["Details"]["SubType"]
        )
        # If current alert's priority is better than worst one, replace the worst alert with current
        if priority < worst_priority:
            for prioritised_alert_index in range(len(prioritised)):
                if worst_priority == convert_alert_to_priority(
                    prioritised[prioritised_alert_index]["Details"]["Type"],
                    prioritised[prioritised_alert_index]["Details"]["SubType"],
                ):
                    prioritised[prioritised_alert_index] = alerts[index]
                    break
            # Update worst for current prioritised
            worst_priority = get_worst_priority(prioritised)

    return [alert["_id"] for alert in prioritised]


def validate_alert(alert: dict) -> bool:
    # Make sure the alert has _id, Details, Type and SubType attributes
    if not all(key in alert for key in ("_id", "Details")):
        return False
    if not all(key in alert["Details"] for key in ("Type", "SubType")):
        return False
    return True


def get_worst_priority(alerts: list) -> int:
    # Find the worst priority value in the alerts list
    worst_priority = 1
    for alert in alerts:
        priority = convert_alert_to_priority(
            alert["Details"]["Type"], alert["Details"]["SubType"]
        )
        worst_priority = priority if priority > worst_priority else worst_priority
    return worst_priority


def convert_alert_to_priority(type: str, subtype: str) -> int:
    # Map type and subtype to value
    mapping = {
        "AttackIndication": {"BlackMarket": 1, "BotDataForSale": 1},
        "DataLeakage": {
            "ConfidentialDocumentLeakage": 4,
            "ConfidentialInformationExposed": 2,
            "CredentialsLeakage": 3,
            "ExposedMentionsOnGithub": 6,
        },
        "vip": {"BlackMarket": 5},
    }
    return mapping[type][subtype]
