from yoomoney import Client
token = "4100118940251415.73747AF94C5DB397A0AA3C2A1FEFDD30DEB8DB519D056996192504FE2BB28925EC3865801328567DBCA1BF9D2E7E0A4A94C3C581805481DE29B25E5711E06BD35CA9B2D8B39CD6DBA9C0A607F9A9A0F82A46A38E271D557D98EA41277A175BBA8613106D7B067DD8BD3CFE4A5A7776554A0A57C332F5D59347D5C74B0DE477E0"
client = Client(token)
history = client.operation_history(label="a1b2c3d4e5")
print("List of operations:")
print("Next page starts with: ", history.next_record)
for operation in history.operations:
    print()
    print("Operation:",operation.operation_id)
    print("\tStatus     -->", operation.status)
    print("\tDatetime   -->", operation.datetime)
    print("\tTitle      -->", operation.title)
    print("\tPattern id -->", operation.pattern_id)
    print("\tDirection  -->", operation.direction)
    print("\tAmount     -->", operation.amount)
    print("\tLabel      -->", operation.label)
    print("\tType       -->", operation.type)
