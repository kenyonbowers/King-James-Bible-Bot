import discord, requests, json, re

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

def Find_Bible_References(text):
    books = {"Genesis": ["gen", "ge", "gn"], "Exodus": ["exo", "ex"], "Leviticus": ["lev", "le"],
             "Numbers": ["num", "nu"], "Deuteronomy": ["deut", "dt"], "Joshua": ["josh", "jsh"], "Judges": ["judg", "jdg"],
             "Ruth": ["rut", "rt"], "1 Samuel": ["1sam", "1 sm", "1samuel"], "2 Samuel": ["2sam", "2 sm", "2samuel"],
             "1 Kings": ["1kgs", "1 ki", "1kings"], "2 Kings": ["2kgs", "2 ki", "2kings"], "1 Chronicles": ["1chr", "1 ch", "1chronicles"],
             "2 Chronicles": ["2chr", "2 ch", "2chronicles"], "Ezra": ["ezr"], "Nehemiah": ["neh", "ne"],
             "Esther": ["est", "et"], "Job": ["job", "jb"], "Psalms": ["ps", "psa"], "Proverbs": ["prov", "pro"],
             "Ecclesiastes": ["eccles", "ecc"], "Song of Solomon": ["sos"], "Isaiah": ["isa", "is"],
             "Jeremiah": ["jer", "je"], "Lamentations": ["lam", "la"], "Ezekiel": ["ezek", "ezk"], "Daniel": ["dan", "dn"],
             "Hosea": ["hos", "ho"], "Joel": ["joel", "jl"], "Amos": ["amos", "am"], "Obadiah": ["obad", "ob"],
             "Jonah": ["jonah", "jn"], "Micah": ["micah", "mic"], "Nahum": ["nah", "na"], "Habakkuk": ["hab", "hk"],
             "Zephaniah": ["zeph", "zp"], "Haggai": ["hag", "hg"], "Zechariah": ["zech", "zc"], "Malachi": ["mal", "ml"],
             "Matthew": ["mt", "matt"], "Mark": ["mk", "mar"], "Luke": ["lk", "luk"], "John": ["jn", "jhn"], "Acts": ["acts"],
             "Romans": ["rom"], "1 Corinthians": ["1cor", "1 corinthians"], "2 Corinthians": ["2cor", "2 corinthians"],
             "Galatians": ["gal"], "Ephesians": ["eph"], "Philippians": ["php"], "Colossians": ["col"],
             "1 Thessalonians": ["1thess", "1 thessalonians"], "2 Thessalonians": ["2thess", "2 thessalonians"],
             "1 Timothy": ["1tim", "1 timothy"], "2 Timothy": ["2tim", "2 timothy"], "Titus": ["titus"],
             "Philemon": ["phlm", "philem"], "Hebrews": ["heb"], "James": ["jas", "jam"], "1 Peter": ["1pet", "1 peter"],
             "2 Peter": ["2pet", "2 peter"], "1 John": ["1jn", "1 john"], "2 John": ["2jn", "2 john"],
             "3 John": ["3jn", "3 john"], "Jude": ["jude"], "Revelation": ["rev"]}

    pattern = r"\b("
    pattern += "|".join(books.keys())
    pattern += r"|"
    pattern += "|".join([abbr for abbrs in books.values() for abbr in abbrs])
    pattern += r")\s+(\d+)(?::(\d+))?(?:-(\d+))?\b"


    regex = re.compile(pattern, re.IGNORECASE)
    matches = regex.findall(text)
    references = []
    for match in matches:
        full_book_name = next((book for book, abbreviations in books.items() if match[0].lower() in abbreviations), match[0])
        references.append((full_book_name, int(match[1]), int(match[2]) if match[2] else None, int(match[3]) if match[3] else None))

    return references

def Get_Passage(book, chapter, start_verse, end_verse):
    url = "https://bible-api.com/"
    if end_verse == 0:
        url += book+"%20"+str(chapter)+":"+str(start_verse)
    else:
        url += book+"%20"+str(chapter)+":"+str(start_verse)+"-"+str(end_verse)
    url += "?translation=kjv"
    JSON = requests.get(url)
    JSON = json.loads(JSON.text)
    return JSON

@client.event
async def on_ready():
    print(f'Logged in as {client.user}!')
    return await client.change_presence(activity=discord.Game(name='Something'))

@client.event
async def on_message(message):
    if message.channel.permissions_for(message.guild.me).send_messages or message.channel.permissions_for(message.guild.me).administrator:
        BibleJson = []
        BibleVerses = Find_Bible_References(message.content)
        for verse in BibleVerses:
            if verse[1] is not None and verse[2] is not None and verse[3] is not None:
                BibleJson.append(Get_Passage(verse[0], verse[1], verse[2], verse[3]))
            elif verse[1] is not None and verse[2] is not None and verse[3] is None:
                BibleJson.append(Get_Passage(verse[0], verse[1], verse[2], 0))
        for Json in BibleJson:
            if "text" in Json:
                desc = ""
                for v in Json["verses"]:
                    desc += "<**"+str(v["verse"])+"**> "+v["text"].strip().replace("\n", " ")+" "
                desc = (desc[:4093] + '...') if len(desc) > 4093 else desc
                embed = discord.Embed(title=":book: ** "+Json["reference"]+" **", description=desc, color=10450525)
                await message.channel.send(embed=embed)
            else:
                embed = discord.Embed(title="There was an Error.", description="There was an error when getting the verse.", color=16711680)
                await message.channel.send(embed=embed)  

client.run('Add_Token_Here')
