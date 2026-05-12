import json
import pytest
from app.utils.chat import is_json_block, make_chat_event


@pytest.mark.parametrize(
    "text, expected",
    [
        ('```json\n{"key": "value"}\n```', True),
        ('```json\n[\n  {"key": "value1"},\n  {"key": "value2"}\n]\n```', True),
        ('```json\n{"key": "value"}', False),
        ("Some random text", False),
        ("```python\nprint('Hello, world!')\n```", False),
        ('```json\n{"key": "value"}\n``` extra text', False),
        ('```json\n{\n  "key": "value",\n  "array": [1, 2, 3]\n}\n```', True),
    ],
)
def test_is_json_block(text, expected):
    assert is_json_block(text) is expected


@pytest.mark.parametrize(
    "text, expected",
    [
        (
            '{"uuid":"96755ad6-ba6b-4c4f-a9cc-775407113363","type":"result","is_error":false,"duration_ms":11643,"duration_api_ms":22199,"num_turns":1,"result":"","session_id":"b48a04be-53aa-4751-9c3b-c01eb387cfd3","total_cost_usd":0.05620125,"usage":{"input_tokens":9,"cache_creation_input_tokens":4347,"cache_read_input_tokens":12671,"output_tokens":555,"server_tool_use":{"web_search_requests":0,"web_fetch_requests":0},"service_tier":"standard","cache_creation":{"ephemeral_1h_input_tokens":0,"ephemeral_5m_input_tokens":4347}}}',
            {
                "event": "end",
                "data": {
                    "duration_ms": 11643,
                    "duration_api_ms": 22199,
                    "is_error": False,
                    "num_turns": 1,
                    "total_cost_usd": 0.05620125,
                    "usage": {
                        "input_tokens": 9,
                        "cache_creation_input_tokens": 4347,
                        "cache_read_input_tokens": 12671,
                        "output_tokens": 555,
                        "server_tool_use": {
                            "web_search_requests": 0,
                            "web_fetch_requests": 0,
                        },
                        "service_tier": "standard",
                        "cache_creation": {
                            "ephemeral_1h_input_tokens": 0,
                            "ephemeral_5m_input_tokens": 4347,
                        },
                    },
                },
            },
        ),
        (
            '{"type":"assistant","message":{"model":"claude-opus-4-5-20251101","id":"msg_01GB337upP2S4V38SW9v1woj","type":"message","role":"assistant","content":[{"type":"text","text":"```json\\n{\\n    \\"project\\": \\"Pretty Hello World\\",\\n    \\"estimated_build_time\\": \\"4 minutes 30 seconds\\",\\n    \\"features\\": [\\n        {\\n            \\"label\\": \\"Hero Section\\",\\n            \\"description\\": \\"Centered Hello World with elegant typography and gradient background\\",\\n            \\"selected\\": true\\n        },\\n        {\\n            \\"label\\": \\"Animated Elements\\",\\n            \\"description\\": \\"Subtle CSS animations on text and floating decorative shapes\\",\\n            \\"selected\\": true\\n        },\\n        {\\n            \\"label\\": \\"Responsive Design\\",\\n            \\"description\\": \\"Mobile-first layout that scales beautifully\\",\\n            \\"selected\\": true\\n},\\n        {\\n            \\"label\\": \\"Modern Color Palette\\",\\n            \\"description\\": \\"Soft gradients with purple-blue tones\\",\\n            \\"selected\\": true\\n        },\\n        {\\n            \\"label\\": \\"Dark/Light Mode Toggle\\",\\n            \\"description\\": \\"Theme switcher with smooth transitions\\",\\n            \\"selected\\": false\\n        },\\n        {\\n            \\"label\\": \\"Particle Background\\",\\n            \\"description\\": \\"Interactive canvas-based particle animation\\",\\n            \\"selected\\": false\\n        }\\n    ]\\n}\\n```"}],"stop_reason":null,"stop_sequence":null,"usage":{"input_tokens":9,"cache_creation_input_tokens":4348,"cache_read_input_tokens":12671,"cache_creation":{"ephemeral_5m_input_tokens":4348,"ephemeral_1h_input_tokens":0},"output_tokens":4,"service_tier":"standard"},"context_management":null},"parent_tool_use_id":null,"session_id":"ec01ad45-345f-4ebe-ae29-106a7553860b","uuid":"d2649c65-9543-4d0f-b510-f0680b2e4682"}',
            {
                "event": "plan",
                "data": {
                    "project": "Pretty Hello World",
                    "estimated_build_time": "4 minutes 30 seconds",
                    "features": [
                        {
                            "label": "Hero Section",
                            "description": "Centered Hello World with elegant typography and gradient background",
                            "selected": True,
                        },
                        {
                            "label": "Animated Elements",
                            "description": "Subtle CSS animations on text and floating decorative shapes",
                            "selected": True,
                        },
                        {
                            "label": "Responsive Design",
                            "description": "Mobile-first layout that scales beautifully",
                            "selected": True,
                        },
                        {
                            "label": "Modern Color Palette",
                            "description": "Soft gradients with purple-blue tones",
                            "selected": True,
                        },
                        {
                            "label": "Dark/Light Mode Toggle",
                            "description": "Theme switcher with smooth transitions",
                            "selected": False,
                        },
                        {
                            "label": "Particle Background",
                            "description": "Interactive canvas-based particle animation",
                            "selected": False,
                        },
                    ],
                },
            },
        ),
        (
            '{"type":"assistant","message":{"model":"claude-opus-4-5-20251101","id":"msg_01GB337upP2S4V38SW9v1woj","type":"message","role":"assistant","content":[{"type":"text","text":"```json\\n{\\n```"}],"stop_reason":null,"stop_sequence":null,"usage":{"input_tokens":9,"cache_creation_input_tokens":4348,"cache_read_input_tokens":12671,"cache_creation":{"ephemeral_5m_input_tokens":4348,"ephemeral_1h_input_tokens":0},"output_tokens":4,"service_tier":"standard"},"context_management":null},"parent_tool_use_id":null,"session_id":"ec01ad45-345f-4ebe-ae29-106a7553860b","uuid":"d2649c65-9543-4d0f-b510-f0680b2e4682"}',
            {
                "event": "error",
                "data": "Unexpected planning error",
            },
        ),
        (
            '{"type":"assistant","message":{"model":"claude-opus-4-5-20251101","id":"msg_0151AHXNx4XH27JbhJ9vUNry","type":"message","role":"assistant","content":[{"type":"text","text":"I will build this beautiful Hello World website with all selected features. Let me start by checking the project structure and then implementing each feature."}],"stop_reason":null,"stop_sequence":null,"usage":{"input_tokens":9,"cache_creation_input_tokens":1720,"cache_read_input_tokens":15031,"cache_creation":{"ephemeral_5m_input_tokens":1720,"ephemeral_1h_input_tokens":0},"output_tokens":4,"service_tier":"standard"},"context_management":null},"parent_tool_use_id":null,"session_id":"ec01ad45-345f-4ebe-ae29-106a7553860b","uuid":"c07d4368-49e4-4020-b493-60d882aeb4df"}',
            {
                "event": "message",
                "data": "I will build this beautiful Hello World website with all selected features. Let me start by checking the project structure and then implementing each feature.",
            },
        ),
        (
            '{"uuid":"96755ad6-ba6b-4c4f-a9cc-775407113363","type":"assistant","message":{"model":"claude-opus-4-5-20251101","id":"msg_01VkX8izYpFNhS9BY4Gtok11","type":"message","role":"assistant","content":[{"type":"tool_use","id":"toolu_01DhTfqVMPeUoa7sWdNsaxeR","name":"TodoWrite","input":{"todos":[{"content":"Hero Section","status":"completed","activeForm":"Building Hero Section"},{"content":"Animated Elements","status":"completed","activeForm":"Adding Animated Elements"},{"content":"About Card","status":"in_progress","activeForm":"Creating About Card"},{"content":"Footer","status":"pending","activeForm":"Building Footer"},{"content":"Dark Mode Toggle","status":"completed","activeForm":"Implementing Dark Mode Toggle"},{"content":"Contact Form","status":"pending","activeForm":"Creating Contact Form"}]}}]}}',
            {
                "event": "progress",
                "data": [
                    {
                        "content": "Hero Section",
                        "status": "completed",
                        "activeForm": "Building Hero Section",
                    },
                    {
                        "content": "Animated Elements",
                        "status": "completed",
                        "activeForm": "Adding Animated Elements",
                    },
                    {
                        "content": "About Card",
                        "status": "in_progress",
                        "activeForm": "Creating About Card",
                    },
                    {
                        "content": "Footer",
                        "status": "pending",
                        "activeForm": "Building Footer",
                    },
                    {
                        "content": "Dark Mode Toggle",
                        "status": "completed",
                        "activeForm": "Implementing Dark Mode Toggle",
                    },
                    {
                        "content": "Contact Form",
                        "status": "pending",
                        "activeForm": "Creating Contact Form",
                    },
                ],
            },
        ),
        (
            '{"type":"queue-operation","operation":"dequeue","timestamp":"2025-12-26T11:12:49.750Z","sessionId":"96755ad6-ba6b-4c4f-a9cc-775407113363"}',
            None,
        ),
        (
            '{"isVisibleInTranscriptOnly":true}',
            None,
        ),
        (
            '{"type":"system"}',
            None,
        ),
    ],
)
def test_make_chat_event(text, expected):
    assert make_chat_event(json.loads(text)) == expected
