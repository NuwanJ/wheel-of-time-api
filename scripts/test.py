import fandom

fandom.set_wiki("wot")
# Source: https://fandom-py.readthedocs.io/en/latest/getting_started.html

page = fandom.page(title="Category:People")

print(page.title)
print(page.content)
