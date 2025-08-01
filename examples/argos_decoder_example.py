from argos import argosMessage

mesg = "66EAB855018A67F8EF3A0000018A23F8EEF20031FFFFFFFFFFFF00000200DD"

decoder = argosMessage.ArgosMessageDecoder()

result = decoder(mesg)

print(f"Argos payload message: {mesg}.")
for k, v in result.items():
    print(f"{k:>20s} : {v}")

