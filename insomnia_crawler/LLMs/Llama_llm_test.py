from groq import Groq

client = Groq(
    
)

chat_completion = client.chat.completions.create(
    messages=[
        {"role": "system", "content": "Transliterate the user's message from greeklish into greek. make sure you output the transliterated text only without anything else. You must follow these rules"},
        {
            "role": "user",
            "content": "Pare epwnymo trofodotiko, estw kai 300w, mporei na se swsei apo polla!! 8a sou proteina na pareis to ANTEC SMARTPOWER 350watt! Exei liges meres pou to phra kai pistevw oti htan mia poly kalh epilogh! Mono 80 eurw, 3 xronia egiisi ta xarakthristika tou ksepernane xalara ena noname 450 watt!!!! Gia tou logou to alithes sou lew oti exei 3,3v kai 5v combined 230watt(oi grammes autes dhl oi 3,3 kai h 5 einai oi shmantikoteres pou prepei na koitas se ena trofodotiko, eidika se platformes Athlon) se anti8esh me kapoio noname 350 watt pou 8a dwsei to poly 180-190 watt! Exei PFC(power factor correction) kati pou dyskola 8a vreis se noname PSU kai systhma diakophs leitourgias se periptwsh yperfwrtwshs!! Gia thn psixi tou yparxoun 2 anemisthres enas 80mm kai enas 92mm pou rithmizoun tis strofes analoga me thn 8ermokrasia! Sto proteinw an psaxneis gia ena poly kalo trofodotiko sta 350watt, pou den kaigetai eukola!! An h tseph sou antexei vevea pare to TRUEPOWER 380 watt, oti kalytero, symfwna me metrhseis vgazei alithina 471 watt!!!! tsekare autes tis dieu8ynseis: , kai Filika"
        }
    ],
    model="llama3-70b-8192",
)

print(chat_completion.choices[0].message.content)
