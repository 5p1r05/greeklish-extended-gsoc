import replicate

# The meta/meta-llama-3-70b-instruct model can stream output as it's running.

prompt = ""
for event in replicate.stream(
    "meta/meta-llama-3-70b-instruct",
    input={
        "prompt": "hello"
    },
):
    print(str(event), end="")