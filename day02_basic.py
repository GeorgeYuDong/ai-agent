nums = []

nums.append(10)
nums.append(20)
nums.append(30)
print("after append: ", nums)

fruits = ["apple", "banana", "orange"]
print("fruits list: ", fruits)

print("===访问数组元素===")
print("first num:", nums[0])
print("first fruit:", fruits[0])

print("nums length:", len(nums))


print("===遍历数组元素===")
for num in nums:
    print(num)


print("===修改数组元素===")
nums[1] = 999
print("after mod:", nums)
