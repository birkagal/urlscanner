# Alerts Cherry-Picking Algorithm

An “alert” is an object with various keys and values. Each alert has the following keys: Alert ID, Type, Subtype, and Title (in reality, there are more, but for the sake of the exercise, we are only using those). Some alerts are more important than others. Each alert based on its keys and identifiers found in the title can be ranked from 1 - highest priority to 6 - lowest.

This algorithm is implemented in the `cherry_pick` function.
The function gets a list of `alerts` and a `num_of_results` which is default to 4 and determines the amount of alerts to pick.

The return value is a list of size `num_of_results`with each element containing a string representing the alert id attribute `_id` of the most prioritize alert in the alerts list.

## Implementation

The algorithm's first step is to check whether the given `num_of_results`is greater than the amount of alerts in the list. If it does it just return the `id`of all alerts present in that list.

Next, the algorithm creates an empty `prioritised` list which would hold the values of the most prioritised alerts. It sets the first `num_of_result`element as the first highest priority alerts and keep track of the `worst_priority` value.

The main loop iterates over the remaining alerts in the list. For each alert, it compares it priority value with the `worst_priority`in the `prioritised`list. If the current alert value is less than the `worst_priority` (Note that value of `1` is the highest priority) we find the index or the alert with `worst_priority`value in the `prioritised`list, switch that alert with the new alert and update `worst_priority`based on the now new `prioritised`list.

After the loop ends, the `prioritised`list now contains `num_of_results`alerts which are heighest priority alerts from the original list.
All left is to extract the id of those alerts and return a list of those ids.

## Complexity

Let's analyze the complexity of the algorithm. The input is a list with `n` alerts, as well as a variable `k`which is the number of results to choose. The default value for `k`is 4.
The first part of the algorithm populates the `prioritised`list with the first `k` elements of the input. It also validates the input and keep track of the `worst_priority`variable. All in all, that loop run in a `O(k)` time.
The second part is the main loop, that iterate over the remaining list and compare each alert with the `prioritised`list to see if a switch is required.
Since `prioritised`has a fixed size which is `k`, the inner loop would take `O(k)`, where the outter loop is running through the list which means the complexity would take `O(n*k)`.

Last, we iterate over `prioritised`once more to extract the ids of the alerts in it, which is once again take `O(k)` time.

All in all, the algorithms complexity is `O(k + n*k + k) => O(n*k)` and if we assume`k=4` we get `O(n)`.
