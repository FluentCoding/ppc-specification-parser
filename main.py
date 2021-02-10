import requests
import json
from bs4 import BeautifulSoup


def text(element):
    child = element.find("strong", recursive=False)
    codeChild = element.find("pre", recursive=False)

    if child is not None:
        return child.text
    elif codeChild is not None:
        return codeChild.find("code", recursive=False).text
    else:
        return element.text


rootUrl = "https://www.ibm.com/support/knowledgecenter/ssw_aix_71/assembler/"

page = requests.get(rootUrl + "idalangref_ins_set.html?view=embed")
soup = BeautifulSoup(page.content, 'html.parser')

links = soup.find("ul", {"class": "ullinks"}).findAll("a")
i = 1

print("Parsed instructions and pages... [1/2]")

result = {}
for link in links:
    instructionPage = requests.get(rootUrl + link.get("href") + "?view=embed")
    instructionSoup = BeautifulSoup(instructionPage.content, 'html.parser')

    instruction = ""
    mnemonics = []
    purpose = ""

    # Fetch instruction and mnemonics
    try:
        instruction = instructionSoup.find("h1", {"class": "topictitle1"}).string.split(maxsplit=1)[0]
    except Exception:
        continue

    instructionEntry = instructionSoup.find("td", text=instruction)
    if instructionEntry is None:
        instructionEntry = instructionSoup.find("strong", text=instruction)
        if instructionEntry is not None:
            instructionEntry = instructionEntry.parent
        # its not my fault that this looks unclean, the language just sucks ass

    if instructionEntry is None or instructionEntry.parent.name != "tr":
        mnemonics = [instruction]
    else:
        for mnemonic in instructionEntry.parent.parent.findAll("tr"):
            mnemonics.append(text(mnemonic.find("td")))

    # Fetch Purpose
    paragraphs = instructionSoup.find("div", {"class": "conbody"}).findAll(["p", "div"], recursive=False)
    purposeFound = False

    for paragraph in paragraphs:
        if purposeFound:
            purpose = text(paragraph)
            break
        elif text(paragraph) == "Purpose":
            purposeFound = True

    result[instruction] = {
        "mnemonics": mnemonics,
        "description": purpose.strip("\n").replace("\n", " ").replace("\u00a0", "").replace("\u00ae", "")
    };
    print("Parsed instruction " + str(i) + " out of " + str(len(links) - 1) + "... [2/2] " + instruction)
    i += 1

with open("result.json", "w") as wf:
    json.dump(result, wf)

print("Done!")