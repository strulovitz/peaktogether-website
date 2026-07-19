import subprocess, sys

with open(r'C:\Users\nir_s\peaktogether-website\press\temp-body.txt', 'r', encoding='utf-8') as f:
    body_template = f.read()

name = sys.argv[1]
email = sys.argv[2]
letter_type = sys.argv[3]

lines = body_template.split('\n')
lines[0] = f'Dear {name},'
body = '\n'.join(lines)

subjects = {
    '1': 'Story: I can\'t write a line of code. I directed AI to build a "Disneyland of mathematics" in one month \u2014 every commit public. (And I spent ten years protesting AI.)',
    '2': 'Story: The most wholesome strange thing on the internet \u2014 a free "Disneyland of mathematics" a non-coder built with AI as a gift for his girlfriend',
    '3': 'Story: The hardest unsolved problems in mathematics, rebuilt as \'90s arcade games \u2014 a free theme park where couples play real university math',
    '4': 'Story: He fought AI for ten years. Then he used it to build a mathematical theme park for the woman he loves \u2014 free, for everyone, forever',
    '5': 'Story: A free, open-source "science museum" where students learn university mathematics by playing \'90s-style games \u2014 no signup, no ads, built by one non-coder with AI'
}
subject = subjects[letter_type]
print(f"Sending v{letter_type} to {name} <{email}>...")
subprocess.run([sys.executable, r'C:\Users\nir_s\gmail-send.py', email, subject, body], check=True)
print(f"OK: {name}")
