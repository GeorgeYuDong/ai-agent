'''
    字典类似于C++ unordered_map
'''
person = {
        "name": "张三",
        "age": 30,
        "Job": "software engineer"
} 

print("完整字典:", person)

print("===根据key取值=====")
print("name:", person.get("name"))
print("age:", person.get("age"))
print("Job:", person.get("Job"))


print("===添加字段=====")
print("===添加字典，不用append, update=====")
person.update({"city": "Shanghai"})
print("city:", person.get("city"))


print("===遍历字典=====")
print("person.items()代表字典的键值对集合")
for key, value in person.items():
    print(key, ":", value)

print("===判断键是否存在=====")
if "Job" in person:
    print("存在Job字段")


