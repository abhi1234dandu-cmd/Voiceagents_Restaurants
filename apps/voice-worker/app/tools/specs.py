TOOL_SPECS = [
    {
        "type": "function",
        "function": {
            "name": "get_hours",
            "description": "Get restaurant hours",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_faq",
            "description": "Search FAQs",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_menu_item",
            "description": "Find menu items",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": "Check reservation availability",
            "parameters": {
                "type": "object",
                "properties": {
                    "starts_at": {"type": "string"},
                    "party_size": {"type": "integer"},
                },
                "required": ["starts_at", "party_size"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_reservation",
            "description": "Create a reservation",
            "parameters": {
                "type": "object",
                "properties": {
                    "guest_name": {"type": "string"},
                    "guest_phone": {"type": "string"},
                    "party_size": {"type": "integer"},
                    "starts_at": {"type": "string"},
                    "notes": {"type": "string"},
                },
                "required": ["guest_name", "guest_phone", "party_size", "starts_at"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_sms_confirmation",
            "description": "Send SMS confirmation",
            "parameters": {
                "type": "object",
                "properties": {
                    "to_number": {"type": "string"},
                    "body": {"type": "string"},
                    "confirmation_code": {"type": "string"},
                },
                "required": ["to_number"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "transfer_to_staff",
            "description": "Transfer call to staff",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "end_call",
            "description": "End the call politely",
            "parameters": {
                "type": "object",
                "properties": {"outcome": {"type": "string"}},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "embed_search",
            "description": "Semantic FAQ/menu retrieval",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
    },
]
