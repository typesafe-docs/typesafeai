"""Verify an agent's tool-call trace with nine atomic checks (one request).

Based on the official "verify a tool-call trace" example. The trace calls get_weather
with unit=celsius although the user asked for Fahrenheit.
"""

from typing import Any

from typesafe_sdk import Noul, TypeSafeClient

STATE: dict[str, Any] = {
    "request": {
        "text": "What's the weather in Seattle tomorrow in Fahrenheit?",
        "location": "Seattle, WA",
        "date": "2026-09-03",
        "unit": "fahrenheit",
    },
    "available_tools": {
        "geocode_city": {"description": "Resolve a city to latitude and longitude.", "parameters": {"city": "string"}},
        "get_weather": {
            "description": "Get the forecast for coordinates and a date.",
            "parameters": {"latitude": "number", "longitude": "number", "date": "YYYY-MM-DD", "unit": ["fahrenheit", "celsius"]},
        },
    },
    "trace": {
        "tool_calls": [
            {"id": "call_1", "name": "geocode_city", "arguments": {"city": "Seattle, WA"}},
            {"id": "call_2", "name": "get_weather",
             "arguments": {"latitude": 47.6062, "longitude": -122.3321, "date": "2026-09-03", "unit": "celsius"}},
        ],
        "tool_results": [{"tool_call_id": "call_1", "output": {"latitude": 47.6062, "longitude": -122.3321}}],
    },
}

CHECKS = {
    "geocode_tool_is_relevant": "Is `trace.tool_calls[0].name` an appropriate tool for resolving `request.location`?",
    "geocode_location_matches": "Does `trace.tool_calls[0].arguments.city` match `request.location`?",
    "geocode_arguments_match_schema": "Does `trace.tool_calls[0].arguments` conform to `available_tools.geocode_city.parameters`?",
    "geocode_result_matches_call": "Does `trace.tool_results[0].tool_call_id` match `trace.tool_calls[0].id`?",
    "weather_tool_is_relevant": "Is `trace.tool_calls[1].name` an appropriate tool for answering `request.text`?",
    "weather_arguments_match_schema": "Does `trace.tool_calls[1].arguments` conform to `available_tools.get_weather.parameters`?",
    "weather_uses_geocoded_coordinates": "Do the coordinates in `trace.tool_calls[1].arguments` match those in `trace.tool_results[0].output`?",
    "weather_date_matches": "Does `trace.tool_calls[1].arguments.date` match `request.date`?",
    "weather_unit_matches": "Does `trace.tool_calls[1].arguments.unit` match `request.unit`?",
}

if __name__ == "__main__":
    with TypeSafeClient() as client:
        answers = client.system_one(
            state=STATE, questions={k: Noul(instructions=q) for k, q in CHECKS.items()}
        ).nouls
    for k in CHECKS:
        v = answers[k].noul
        print(f"{'PASS' if v >= 0.5 else 'FAIL'}  {v:4.2f}  {k}")
