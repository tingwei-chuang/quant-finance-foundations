"""Builder for the Week 6 notebook — English edition.

Generated content mirrors ``week6.py`` (the Traditional Chinese original) cell
for cell; only the natural language differs. See
scripts/_notebook_lib/__init__.py for the dispatch table.
"""

from __future__ import annotations

import nbformat as nbf

from .cells import code, ex_code, md
from .parts_en import (
    checklist_en,
    exercises_intro_en,
    footer_references_en,
    header_en,
    mistakes_en,
    quiz_cells_en,
)


def week(solution: bool) -> list[nbf.NotebookNode]:
    cells = header_en(
        solution=solution,
        week="Week 6",
        title="Financial Mathematics and Option Pricing",
        objectives=[
            "Compute discount factors, present values, and bond prices.",
            "Plot payoff diagrams for calls, puts, and simple combinations.",
            "Price European options with a binomial tree.",
            "Run sensitivity analyses over strike, volatility, maturity, and interest rate.",
        ],
        hours="8–10 hours",
        prereqs=["Basic algebra and exponents", "Return concepts from Week 1"],
        resources=[
            (
                "NTU OpenCourseWare: Fundamentals of Financial Literacy",
                "https://ocw.aca.ntu.edu.tw/courses/110S204",
            ),
        ],
    )
    cells += [
        md(
            "## Concepts\n\n"
            "### The time value of money\n\n"
            "A future cash flow must be **discounted** before it can be compared "
            "with money today. With annual rate $r$, $t$ years out, compounded "
            "$m$ times per year, the discount factor is $(1 + r/m)^{-mt}$. The "
            "present value is the sum of each cash flow times its discount "
            "factor.\n\n"
            "### Option payoffs and binomial pricing\n\n"
            "At expiry, a European call/put pays $\\max(S-K,0)$, $\\max(K-S,0)$.\n\n"
            "This roadmap **deliberately uses only the binomial tree**: it needs "
            "nothing beyond arithmetic and the no-arbitrage idea — **no** "
            "stochastic calculus, and **no** Black-Scholes derivation required. "
            "The option value is the discounted expected value of its expiry "
            "payoff under the risk-neutral probability.\n\n"
            "> Reminder: model prices should **not** be read as forecasts of "
            "real market prices."
        ),
        code(
            "import numpy as np\n"
            "import matplotlib.pyplot as plt\n"
            "from quant_math_roadmap.finance.fixed_income import (\n"
            "    bond_price, discount_factor, present_value, zero_coupon_bond_price,\n"
            ")\n"
            "from quant_math_roadmap.finance.derivatives import (\n"
            "    binomial_european_option, call_payoff, put_payoff,\n"
            "    long_straddle_payoff, put_call_parity_gap,\n"
            ")"
        ),
        md("### A present-value calculator"),
        code(
            "rate = 0.04\n"
            "cash_flows = [100, 100, 100, 1100]  # 4-year bond, annual coupons\n"
            "times = [1, 2, 3, 4]\n"
            "pv = present_value(cash_flows, times, rate)\n"
            "print(f'At a {rate:.0%} discount rate, the present value of the cash flows = {pv:.2f}')\n"
            "for t in times:\n"
            "    print(f'  t={t}: discount factor = {discount_factor(rate, t):.4f}')"
        ),
        md("### Bond pricing: price falls as the yield rises"),
        code(
            "yields = np.linspace(0.01, 0.10, 50)\n"
            "prices = [bond_price(1000, 0.05, 10, y, coupons_per_year=2) for y in yields]\n"
            "\n"
            "fig, ax = plt.subplots(figsize=(8, 4.5))\n"
            "ax.plot(yields, prices, label='10-year, 5% coupon bond')\n"
            "ax.axhline(1000, linestyle='--', label='Face value = 1000')\n"
            "ax.set_title('Bond price vs yield')\n"
            "ax.set_xlabel('Yield to maturity')\n"
            "ax.set_ylabel('Bond price')\n"
            "ax.legend()\n"
            "plt.show()\n"
            "zcb = zero_coupon_bond_price(1000, 10, 0.05)\n"
            "print(f'Price of a 10-year zero-coupon bond (5% yield) = {zcb:.2f}')"
        ),
        md(
            "As the yield rises, the bond price falls; when the coupon rate "
            "equals the yield, the bond prices at par (face value)."
        ),
        md(
            "### Duration and convexity: a bond's interest-rate sensitivity\n\n"
            "Knowing how the price moves with the yield is more useful than "
            "knowing a single price:\n\n"
            "- **Macaulay duration**: the present-value-weighted average arrival "
            "time of the cash flows (in years). For a zero-coupon bond the "
            "duration equals the maturity exactly.\n"
            "- **Modified duration** $D_{mod} = -\\frac{1}{P}\\frac{dP}{dy}$: "
            "for each percentage-point move in the yield, the price moves by "
            "roughly $D_{mod}$%.\n"
            "- **Convexity** $C = \\frac{1}{P}\\frac{d^2P}{dy^2}$: the curvature "
            "correction; the second-order approximation is "
            "$\\Delta P/P \\approx -D_{mod}\\Delta y + \\tfrac12 C (\\Delta y)^2$."
        ),
        code(
            "from quant_math_roadmap.finance.fixed_income import (\n"
            "    bond_convexity, macaulay_duration, modified_duration,\n"
            ")\n"
            "\n"
            "args = dict(face_value=1000, coupon_rate=0.05,\n"
            "            years_to_maturity=10, yield_to_maturity=0.04)\n"
            "mac = macaulay_duration(**args)\n"
            "mod = modified_duration(**args)\n"
            "conv = bond_convexity(**args)\n"
            "print(f'Macaulay duration = {mac:.4f} years')\n"
            "print(f'Modified duration = {mod:.4f}')\n"
            "print(f'Convexity         = {conv:.4f}')\n"
            "\n"
            "# Check what these numbers mean: true repricing vs first/second-order approximations\n"
            "p0 = bond_price(1000, 0.05, 10, 0.04, coupons_per_year=2)\n"
            "dy = 0.01  # yield +100bp\n"
            "p1 = bond_price(1000, 0.05, 10, 0.04 + dy, coupons_per_year=2)\n"
            "actual = p1 / p0 - 1\n"
            "first_order = -mod * dy\n"
            "second_order = -mod * dy + 0.5 * conv * dy**2\n"
            "print(f'Actual price change          = {actual:+.4%}')\n"
            "print(f'First order (duration)       = {first_order:+.4%}')\n"
            "print(f'Second order (+convexity)    = {second_order:+.4%}  <- closer to the actual change')"
        ),
        md(
            "Zero-coupon check: `macaulay_duration(1000, 0.0, 5, 0.04, coupons_per_year=1)`"
            " returns exactly 5.0 years — the only cash flow arrives at maturity."
        ),
        md("### Payoff diagrams"),
        code(
            "spot_grid = np.linspace(50, 150, 200)\n"
            "strike = 100.0\n"
            "fig, axes = plt.subplots(1, 3, figsize=(13, 4))\n"
            "axes[0].plot(spot_grid, call_payoff(spot_grid, strike))\n"
            "axes[0].set_title('Call payoff (K=100)')\n"
            "axes[1].plot(spot_grid, put_payoff(spot_grid, strike))\n"
            "axes[1].set_title('Put payoff (K=100)')\n"
            "axes[2].plot(spot_grid, long_straddle_payoff(spot_grid, strike))\n"
            "axes[2].set_title('Long straddle payoff (K=100)')\n"
            "for ax in axes:\n"
            "    ax.set_xlabel('Underlying price at expiry S')\n"
            "    ax.set_ylabel('payoff')\n"
            "plt.tight_layout()\n"
            "plt.show()"
        ),
        md("### Binomial European option pricing"),
        code(
            "params = {'spot': 100.0, 'strike': 100.0, 'rate': 0.05,\n"
            "          'volatility': 0.20, 'maturity': 1.0}\n"
            "call = binomial_european_option(**params, n_steps=300, option_type='call')\n"
            "put = binomial_european_option(**params, n_steps=300, option_type='put')\n"
            "print(f'European call price = {call:.4f}')\n"
            "print(f'European put  price = {put:.4f}')\n"
            "gap = put_call_parity_gap(call, put, params['spot'], params['strike'],\n"
            "                          params['rate'], params['maturity'])\n"
            "print(f'put-call parity residual = {gap:.6f}  (should be close to 0)')"
        ),
        md("### Sensitivity analysis"),
        code(
            "vols = np.linspace(0.05, 0.6, 40)\n"
            "call_by_vol = [binomial_european_option(100, 100, 0.05, v, 1.0,\n"
            "               n_steps=200) for v in vols]\n"
            "\n"
            "fig, ax = plt.subplots(figsize=(8, 4.5))\n"
            "ax.plot(vols, call_by_vol, label='ATM call (S=K=100)')\n"
            "ax.set_title('European call price vs volatility')\n"
            "ax.set_xlabel('Volatility proxy sigma')\n"
            "ax.set_ylabel('Call price')\n"
            "ax.legend()\n"
            "plt.show()\n"
            "print('Higher volatility makes the option more expensive — greater uncertainty benefits the buyer.')"
        ),
        md(
            "### American options: the difference one max makes\n\n"
            "An American option can be **exercised early**. On a binomial tree, "
            "that just changes the backward-induction value at each node to "
            "`max(discounted expected continuation value, immediate exercise value)`. "
            "Two classic results can be verified numerically:\n\n"
            "1. **An American call on a non-dividend-paying underlying equals "
            "the European call** (early exercise never pays);\n"
            "2. **An American put ≥ the European put** (deep in the money, "
            "receiving the strike early has time value)."
        ),
        code(
            "from quant_math_roadmap.finance.derivatives import binomial_american_option\n"
            "\n"
            "common = dict(spot=100.0, strike=110.0, rate=0.06,\n"
            "              volatility=0.2, maturity=2.0, n_steps=300)\n"
            "eu_call = binomial_european_option(option_type='call', **common)\n"
            "am_call = binomial_american_option(option_type='call', **common)\n"
            "eu_put = binomial_european_option(option_type='put', **common)\n"
            "am_put = binomial_american_option(option_type='put', **common)\n"
            "print(f'European call = {eu_call:.4f} | American call = {am_call:.4f}  (equal)')\n"
            "print(f'European put  = {eu_put:.4f} | American put  = {am_put:.4f}  (American is worth more)')\n"
            "print(f'Early-exercise premium of the American put = {am_put - eu_put:.4f}')"
        ),
        md(
            "### Greeks: price sensitivity to each input\n\n"
            "The **Greeks** answer the question: if one input moves a little, how "
            "much does the price move? `binomial_greeks()` estimates them "
            "directly on the tree with finite differences:\n\n"
            "| Greek | Definition | Intuition |\n"
            "|-------|------|------|\n"
            "| delta | ∂V/∂S | how much the option gains when the underlying rises by 1 |\n"
            "| gamma | ∂²V/∂S² | how fast delta itself changes |\n"
            "| vega  | ∂V/∂σ | impact of a 1-unit rise in volatility |\n"
            "| theta | −∂V/∂T | decay from one year of time passing |\n"
            "| rho   | ∂V/∂r | impact of a 1-unit rise in the rate |\n\n"
            "> Finite differences on a tree are an approximation of an "
            "approximation — the numbers jitter slightly. This is a teaching "
            "tool, not a production-grade pricer."
        ),
        code(
            "from quant_math_roadmap.finance.derivatives import binomial_greeks\n"
            "\n"
            "greeks_call = binomial_greeks(100, 100, 0.05, 0.2, 1.0, option_type='call')\n"
            "greeks_put = binomial_greeks(100, 100, 0.05, 0.2, 1.0, option_type='put')\n"
            "for name in ['delta', 'gamma', 'vega', 'theta', 'rho']:\n"
            "    print(f'{name:>6}: call = {greeks_call[name]:>9.4f} | put = {greeks_put[name]:>9.4f}')\n"
            "print()\n"
            "print(f'delta_call - delta_put = {greeks_call['delta'] - greeks_put['delta']:.6f}'\n"
            "      '  (put-call parity says this difference is exactly 1)')"
        ),
        exercises_intro_en(),
        md(
            "### Basic exercises\n\n"
            "1. In one sentence, explain why future money must be discounted.\n"
            "2. Why do bond prices and yields move in opposite directions?\n"
            "3. Describe the shape of a long straddle payoff and what it is betting on."
        ),
        md("### Applied exercises"),
        ex_code(
            solution,
            prompt=(
                "# Applied exercise 1: compute the binomial call price as a function of strike (other parameters fixed),\n"
                "# and confirm that a higher strike makes the call cheaper."
            ),
            starter=(
                "strikes = np.linspace(80, 120, 20)\n"
                "call_by_strike = None  # TODO: [binomial_european_option(100, k, 0.05, 0.2, 1.0, n_steps=150) for k in strikes]\n"
                "if call_by_strike is not None:\n"
                "    print('Decreasing?', all(np.diff(call_by_strike) < 0))"
            ),
            answer=(
                "strikes = np.linspace(80, 120, 20)\n"
                "call_by_strike = [binomial_european_option(100, k, 0.05, 0.2, 1.0,\n"
                "                  n_steps=150) for k in strikes]\n"
                "print('Higher strike, cheaper call?', all(np.diff(call_by_strike) < 0))"
            ),
        ),
        ex_code(
            solution,
            prompt=(
                "# Applied exercise 2: verify that the binomial call price converges (settles down) as the step count grows."
            ),
            starter=(
                "for steps in [10, 50, 200, 800]:\n"
                "    price = None  # TODO: binomial_european_option(100, 100, 0.05, 0.2, 1.0, n_steps=steps)\n"
                "    print(steps, price)"
            ),
            answer=(
                "for steps in [10, 50, 200, 800]:\n"
                "    price = binomial_european_option(100, 100, 0.05, 0.2, 1.0,\n"
                "                                     n_steps=steps)\n"
                "    print(f'n_steps={steps:>3}: call = {price:.4f}')\n"
                "print('More steps, more stable price (convergence).')"
            ),
        ),
        md(
            "### Reflection question\n\n"
            "1. Binomial model prices almost never match real market prices "
            "exactly. What caution does this suggest for designing trading "
            "strategies around model prices?"
        ),
        *quiz_cells_en(
            solution,
            week=6,
            items=[
                (
                    "When the yield rises, the bond price?",
                    ["Rises", "Falls", "Stays the same", "Depends on the coupon"],
                    "B",
                    "Future cash flows are discounted at a higher rate, so the present value must fall — the first law of bond pricing.",
                ),
                (
                    "The Macaulay duration of a zero-coupon bond equals?",
                    ["0", "The years to maturity", "The yield to maturity", "The coupon rate"],
                    "B",
                    "There is a single cash flow at maturity, so the weighted-average arrival time is the maturity itself.",
                ),
                (
                    "For a non-dividend-paying underlying, the American call price relative to the European call is?",
                    ["Higher", "Equal", "Lower", "It depends"],
                    "B",
                    "Early exercise gives up time value with no dividends to collect, so it never pays — the two are equivalent.",
                ),
                (
                    "What does positive convexity mean?",
                    [
                        "When yields fall, the price gain exceeds the linear duration estimate",
                        "Price is proportional to yield",
                        "The bond has default risk",
                        "Duration is negative",
                    ],
                    "A",
                    "The price-yield curve is convex: the price falls by less than the linear estimate and rises by more.",
                ),
            ],
        ),
        mistakes_en(
            [
                "Mixing up compounding frequencies when discounting (annual vs semiannual).",
                "Confusing the option payoff (realized only at expiry) with the option price today.",
                "Treating the binomial price as exact when the step count is too small.",
                "Claiming the model price equals the real market price.",
            ]
        ),
        checklist_en(
            [
                "Compute present values and bond prices.",
                "Plot and interpret call/put/straddle payoff diagrams.",
                "Price a European option with a binomial tree and explain each step.",
                "Run sensitivity analyses over the main parameters.",
            ]
        ),
        footer_references_en(solution),
    ]
    return cells
