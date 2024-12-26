from yoomoney import Authorize

Authorize(
    client_id="C66E9C2FC330176923EFC49F130679FF18819ECFB8659577C4D2919AD01ABD46",
    redirect_uri="http://alice.ru",
    client_secret="alice_secret",
    scope=["account-info",
           "operation-history",
           "operation-details",
           "incoming-transfers",
           "payment-p2p",
           "payment-shop",
           ]
)
