import livekit.plugins.silero as silero
import inspect

print("Silero members:")
for name, obj in inspect.getmembers(silero):
    if inspect.isclass(obj):
        print(f"Class: {name}")
    elif inspect.ismodule(obj):
        print(f"Module: {name}")
    else:
        print(f"Member: {name}")
