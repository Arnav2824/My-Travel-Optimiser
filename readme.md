
# Travel Optimiser

An intelligent travel optimisation engine that evaluates multiple travel options and recommends the best journey based on a user's priorities, constraints, availability, freshness, cost, time, and convenience.

The goal is not simply to find the cheapest or fastest ticket.

The goal is to answer:

> **"Given what I care about, what is the best way for me to get from A to B?"**

---

## 🚧 Project Status

**Currently in development**

The core optimisation engine and provider architecture are being built and tested before integrating real-world travel data providers.

Current test suite:

**85 tests passing**

---

## 🎯 What This Project Does

A user provides:

- Origin
- Destination
- Travel date
- Budget
- Cost preference
- Time preference
- Convenience preference
- Maximum transfers
- Departure/arrival constraints
- Value of time

The system then:

1. Collects travel options from providers
2. Validates provider output
3. Combines results from multiple providers
4. Removes duplicate options
5. Handles provider priority
6. Filters unavailable options
7. Filters stale travel data
8. Generates possible journeys
9. Applies user constraints
10. Removes dominated journeys
11. Ranks the remaining journeys
12. Selects the best recommendation
13. Generates an explanation for the recommendation

---

## 🧠 Core Idea

Traditional travel platforms primarily help users **search and book**.

Travel Optimiser is being designed around a different problem:

> **Decision-making across multiple travel options.**

For example, instead of simply showing:

| Option | Price | Duration |
|---|---:|---:|
| Flight | ₹5,000 | 2h |
| Train | ₹1,500 | 18h |
| Bus | ₹1,000 | 20h |

the system attempts to understand the user's priorities.

A user who heavily values time may receive the flight.

A budget-conscious user may receive the train.

A user who strongly dislikes transfers may receive a different option entirely.

The recommendation is therefore **preference-driven rather than universally optimal**.

---

## 🏗️ Architecture

The current architecture is structured around separate responsibilities:

```text
                    Travel Request
                          │
                          ▼
                    FastAPI API
                          │
                          ▼
                 Travel Data Manager
                          │
             ┌────────────┼────────────┐
             ▼            ▼            ▼
         Provider 1   Provider 2   Provider 3
             │            │            │
             └────────────┼────────────┘
                          ▼
                     Travel Legs
                          │
                          ▼
                  Journey Generator
                          │
                          ▼
               Availability Filter
                          │
                          ▼
                  Freshness Filter
                          │
                          ▼
                 Constraint Filter
                          │
                          ▼
                Dominance Filtering
                          │
                          ▼
                     Ranking
                          │
                          ▼
                  Recommendation
                          │
                          ▼
                 Explanation Engine
                          │
                          ▼
                     API Response