#!/usr/bin/env python3
"""Check ZIP candidate arithmetic with Fraction, not native consensus validation."""

import json
import sys
from fractions import Fraction
from pathlib import Path

Q = 100_000_000
UNIT = 1_000_000
MAX_C = 21_000_000 * Q
CAP = 100_000 * UNIT
MIN_DEBT = 100 * UNIT
U64_MAX = (1 << 64) - 1
U128_MAX = (1 << 128) - 1
PARAMETERS = {
    "zatoshi_per_zec": Q,
    "micro_units_per_zusd": UNIT,
    "max_collateral": MAX_C,
    "max_price": U64_MAX,
    "min_nonzero_principal": MIN_DEBT,
    "supply_cap": CAP,
    "borrow_ratio": "5/2",
    "liquidation_ratio": "2/1",
    "liquidation_payout_multiplier": "21/20",
    "intermediate_bits": 128,
}
FIELDS = {
    "open": {"collateral", "principal", "supply", "bad_debt", "price", "oracle_fresh"},
    "update": {"collateral", "principal", "new_collateral", "new_principal", "supply", "bad_debt", "price", "oracle_fresh", "stable_input"},
    "close": {"collateral", "principal", "supply", "bad_debt", "stable_input"},
    "liquidate": {"collateral", "principal", "supply", "bad_debt", "price", "oracle_fresh", "stable_input", "max_burn", "min_collateral"},
    "retire_bad_debt": {"supply", "bad_debt", "amount", "stable_input"},
}


class Invalid(ValueError):
    """A financial precondition failed; no state is committed."""


def require(condition, reason):
    if not condition:
        raise Invalid(reason)


def bounded(value, limit):
    require(type(value) is int and 0 <= value <= limit, "range")


def debt_valid(value):
    return value == 0 or value >= MIN_DEBT


def price_for(data):
    require(data["oracle_fresh"] and data["price"] is not None, "oracle")
    return Fraction(data["price"], Q)


def enough_collateral(collateral, principal, price):
    return collateral * price >= Fraction(5, 2) * principal


def post(supply, bad_debt, collateral, principal, minted=0, burned=0,
         deposit=0, owner=0, liquidator=0):
    return {
        "accepted": True,
        "supply": supply,
        "bad_debt": bad_debt,
        "vault": None if collateral is None else {"collateral": collateral, "principal": principal},
        "minted": minted,
        "burned": burned,
        "zec_deposited": deposit,
        "owner_zec": owner,
        "liquidator_zec": liquidator,
    }


def evaluate(operation, data):
    if operation not in FIELDS or set(data) != FIELDS[operation]:
        raise ValueError("unknown operation or input fields")
    try:
        for name, value in data.items():
            if name == "oracle_fresh":
                require(type(value) is bool, "range")
            elif name == "price":
                if value is not None:
                    bounded(value, U64_MAX)
                    require(value > 0, "range")
            else:
                limit = MAX_C if "collateral" in name else U64_MAX if name == "max_burn" else CAP
                bounded(value, limit)
        supply, bad = data["supply"], data["bad_debt"]
        require(bad <= supply, "prestate")
        collateral, debt = data.get("collateral", 0), data.get("principal", 0)
        if operation not in {"open", "retire_bad_debt"}:
            require(collateral > 0 and debt_valid(debt) and supply >= debt + bad, "prestate")
        other_principal = supply - bad - (debt if operation not in {"open", "retire_bad_debt"} else 0)
        require(debt_valid(other_principal), "prestate")
        if "stable_input" in data:
            require(data["stable_input"] <= supply, "prestate")

        if operation == "open":
            require(collateral > 0, "collateral")
            require(debt_valid(debt), "minimum_debt")
            if debt:
                require(bad == 0, "bad_debt_freeze")
                require(enough_collateral(collateral, debt, price_for(data)), "collateral_ratio")
            require(supply + debt <= CAP, "supply_cap")
            return post(supply + debt, bad, collateral, debt, minted=debt, deposit=collateral)

        if operation == "update":
            new_c, new_d = data["new_collateral"], data["new_principal"]
            require(new_c > 0, "collateral")
            require((new_c, new_d) != (collateral, debt), "no_change")
            require(debt_valid(new_d), "minimum_debt")
            if new_d > debt:
                require(bad == 0, "bad_debt_freeze")
            if new_d > debt or (new_c < collateral and new_d > 0):
                require(enough_collateral(new_c, new_d, price_for(data)), "collateral_ratio")
            burn, mint = max(0, debt - new_d), max(0, new_d - debt)
            require(burn <= data["stable_input"], "stable_input")
            require(supply + mint <= CAP, "supply_cap")
            return post(supply + mint - burn, bad, new_c, new_d, minted=mint, burned=burn,
                        deposit=max(0, new_c - collateral), owner=max(0, collateral - new_c))

        if operation == "close":
            require(debt <= data["stable_input"], "stable_input")
            return post(supply - debt, bad, None, None, burned=debt, owner=collateral)

        if operation == "liquidate":
            require(debt > 0, "healthy")
            price = price_for(data)
            require(collateral * price < 2 * debt, "healthy")
            # Fraction derives affordability and payout independently of the ZIP's
            # cross-multiplied integer formulas.
            affordable = collateral * price / Fraction(21, 20)
            burn = min(debt, affordable.numerator // affordable.denominator)
            payment = Fraction(burn) * Fraction(21, 20) / price
            paid = -(-payment.numerator // payment.denominator)
            require(paid <= collateral, "collateral")
            require(burn <= data["stable_input"], "stable_input")
            require(burn <= data["max_burn"] and paid >= data["min_collateral"], "intent_bounds")
            require(supply - burn == (supply - debt - bad) + (bad + debt - burn), "liability_invariant")
            if burn < debt:
                require((collateral - paid) * price < Fraction(21, 20), "rounding_invariant")
            return post(supply - burn, bad + debt - burn, None, None, burned=burn,
                        owner=collateral - paid, liquidator=paid)

        amount = data["amount"]
        require(amount > 0 and amount <= bad, "retirement_amount")
        require(amount <= data["stable_input"], "stable_input")
        require((supply - amount) - (bad - amount) == supply - bad, "liability_invariant")
        return {"accepted": True, "supply": supply - amount, "bad_debt": bad - amount,
                "burned": amount, "zec_payout": 0, "live_principal": supply - bad}
    except Invalid as error:
        return {"accepted": False, "reason": str(error)}


def check(path):
    document = json.loads(path.read_text())
    if document["format"] != "zsv-zip-financial-vectors-v1":
        raise ValueError("unsupported vector format")
    if document["parameters"] != PARAMETERS:
        raise ValueError("parameter mismatch")
    # This domain cannot overflow the specified unsigned 128-bit intermediates.
    assert MAX_C * U64_MAX * 100 <= U128_MAX
    assert CAP * Q * 250 <= U128_MAX
    assert CAP * Q * 105 <= U128_MAX
    names = set()
    for case in document["cases"]:
        if case["id"] in names:
            raise ValueError(f"duplicate case {case['id']}")
        names.add(case["id"])
        if type(case["expected"]["accepted"]) is not bool:
            raise ValueError(f"{case['id']}: accepted must be boolean")
        actual = evaluate(case["operation"], case["input"])
        if actual != case["expected"]:
            raise ValueError(f"{case['id']}: expected {case['expected']}, computed {actual}")
    print(f"Financial ZIP vectors checked: {len(names)} cases; exact Fraction arithmetic and u128 bounds.")


if __name__ == "__main__":
    if len(sys.argv) > 2:
        sys.exit("usage: check_financial_vectors.py [vectors.json]")
    try:
        check(Path(sys.argv[1]) if len(sys.argv) == 2 else Path(__file__).with_name("financial-vectors.json"))
    except (KeyError, ValueError, AssertionError) as error:
        sys.exit(str(error))
