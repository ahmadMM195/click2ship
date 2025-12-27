import frappe

@frappe.whitelist(allow_guest=True)
def get_trucking_quotes(
    terms=None,
    mode=None,
    type_=None,
    from_location=None,
    to_location=None,
    equipment=None,
    empty_return=0
):
    """
    Public API to fetch trucking quotes based on tariff
    """

    filters = {
        "docstatus": 0
    }
    if terms:
        filters["terms"] = terms
    if mode:
        filters["mode"] = mode
    if type_:
        filters["type"] = type_
    if from_location:
        filters["from_location"] = from_location
    if to_location:
        filters["to_location"] = to_location
    if equipment:
        filters["equipment"] = equipment
    if empty_return is not None:
        filters["empty_return"] = int(empty_return)
    print("333333333333333tariffs33333333333333333")
    print(from_location)
    print(to_location)
    print(filters)
    tariffs = frappe.get_all(
        "Trucking Tariff",
        filters=filters,
        fields=[
            "name",
            "terms",
            "mode",
            "type",
            "from_location",
            "to_location",
            "equipment",
            "empty_return"
        ]
    )
    print(tariffs)

    if not tariffs:
        return {
            "status": "error",
            "message": "No trucking tariff found"
        }

    results = []
    print("4444444444444444")
    print(tariffs)
    for tariff in tariffs:
        rates = frappe.get_all(
            "Trucking Rate Detail",
            filters={
                "parent": tariff.name,
                "parenttype": "Trucking Tariff",
                "parentfield": "rates"
            },
            fields=[
                "capacity",
                "vehicle_description",
                "rate"
            ]
        )

        results.append({
            "tariff": tariff,
            "rates": rates
        })
    print("555555555555555555")
    print(results)
    return {
        "status": "success",
        "count": len(results),
        "data": results
    }

