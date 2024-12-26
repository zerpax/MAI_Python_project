from yoomoney import Client
token = "4100118940251415.73747AF94C5DB397A0AA3C2A1FEFDD30DEB8DB519D056996192504FE2BB28925EC3865801328567DBCA1BF9D2E7E0A4A94C3C581805481DE29B25E5711E06BD35CA9B2D8B39CD6DBA9C0A607F9A9A0F82A46A38E271D557D98EA41277A175BBA8613106D7B067DD8BD3CFE4A5A7776554A0A57C332F5D59347D5C74B0DE477E0"
client = Client(token)
user = client.account_info()
print("Account number:", user.account)
print("Account balance:", user.balance)
print("Account currency code in ISO 4217 format:", user.currency)
print("Account status:", user.account_status)
print("Account type:", user.account_type)
print("Extended balance information:")
for pair in vars(user.balance_details):
    print("\t-->", pair, ":", vars(user.balance_details).get(pair))
print("Information about linked bank cards:")
cards = user.cards_linked
if len(cards) != 0:
    for card in cards:
        print(card.pan_fragment, " - ", card.type)
else:
    print("No card is linked to the account")

