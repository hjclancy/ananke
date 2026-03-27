def run_agent(user_message: str):
    messages = [{"role": "user", "content": user_message}]

    system = """You are a portfolio assistant managing a Robinhood account.
    You can look up prices, check holdings, and place trades.
    IMPORTANT: Before placing any order, always summarize what you're about to do
    and ask the user to confirm. Never place a trade without explicit approval."""

    while True:
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=1024,
            system=system,
            tools=tools,
            messages=messages
        )

        # Append Claude's response to history
        messages.append({"role": "assistant", "content": response.content})

        # If Claude is done, print and exit
        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    print(f"\nAssistant: {block.text}")
            break

        # Handle tool calls
        if response.stop_reason == "tool_use":
            tool_results = []

            for block in response.content:
                if block.type == "tool_use":
                    print(f"\n[Calling tool: {block.name} with {block.input}]")

                    # --- Human-in-the-loop for orders ---
                    if block.name == "place_market_order":
                        confirm = input(f"Confirm {block.input['side'].upper()} "
                                        f"{block.input['quantity']} shares of "
                                        f"{block.input['symbol']}? (yes/no): ")
                        if confirm.lower() != "yes":
                            result = {"error": "Order cancelled by user."}
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": json.dumps(result)
                            })
                            continue

                    # Execute the tool
                    tool_map = {
                        "get_portfolio": get_portfolio,
                        "get_quote": lambda: get_quote(block.input["symbol"]),
                        "get_account_info": get_account_info,
                        "place_market_order": lambda: place_market_order(**block.input)
                    }

                    try:
                        result = tool_map[block.name]()
                    except Exception as e:
                        result = {"error": str(e)}

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result)
                    })

            messages.append({"role": "user", "content": tool_results})

# Run it
if __name__ == "__main__":
    login()
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        run_agent(user_input)
```

---

## Example Interactions
```
You: What's my portfolio look like?
[Calling tool: get_portfolio]
Assistant: You hold 10 shares of AAPL (avg cost $172.50) and 5 shares of NVDA (avg cost $430.00).

You: What's Apple trading at right now?
[Calling tool: get_quote with {'symbol': 'AAPL'}]
Assistant: AAPL is currently trading at $189.42.

You: Buy 2 shares of AAPL
Assistant: I'd like to place a market buy order for 2 shares of AAPL at ~$189.42 each (~$378.84 total). Shall I proceed?
You: yes
Confirm BUY 2 shares of AAPL? (yes/no): yes
[Calling tool: place_market_order]
Assistant: Order placed successfully.
