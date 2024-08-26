# Original list of numbers
numbers = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3]

# Using the sorted() function (returns a new sorted list)
sorted_numbers = sorted(numbers)
print("Original list after using sorted():", numbers)
print("New sorted list:", sorted_numbers)

# Using the sort() method (sorts the list in place)
numbers.sort()
print("Original list after using sort():", numbers)

Original list after using sorted(): [3, 1, 4, 1, 5, 9, 2, 6, 5, 3]
New sorted list: [1, 1, 2, 3, 3, 4, 5, 5, 6, 9]
Original list after using sort(): [1, 1, 2, 3, 3, 4, 5, 5, 6, 9]

When to Use Each:
Use sorted() when you need a sorted version of the original data but want to keep the original data unchanged.
Use sort() when you need to sort the data in place and do not need to keep the original order
