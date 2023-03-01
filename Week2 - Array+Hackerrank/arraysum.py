# Using a for loop initialize a variable, total_sum=0
# Iterate through the array & add each element to initialized variable, total_sum
def array_sum(ar):
    total_sum = 0

    for i in ar:
        total_sum += i

    return total_sum    


# Feed the array_sum function an array arguement & print output
ar = [1, 2, 3]
print(array_sum(ar))