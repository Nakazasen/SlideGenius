
import google.generativeai as genai

print("SDK Version:", genai.__version__)
print("\nAttributes of genai:")
print(dir(genai))

try:
    model = genai.GenerativeModel("imagen-3.0-generate-001")
    print("\nAttributes of GenerativeModel:")
    print(dir(model))
except Exception as e:
    print(e)
