Aktiva AI - A Self Hosted AI Discord Bot

Big thank you to @badgids for making this possible, hehe~

## FEATURES!!!

### Seamless Character Swapping
- There is only one slash command, and that is to bring up the character list!
- Because you only need to say a character's name or answer to their reply
- All characters uses Webhooks! So different avatar for different name~
- Adding character is as easy as making a json and putting them in the characters folder! (refer to character MD file please)
  
### Image Recognition
- Uses the all new [Microsoft's Florence 2 AI](https://huggingface.co/microsoft/Florence-2-base-ft) for object recognition
- Uses Llava by default for vibe detection
- Combined, this puppy can *almost* beat most Open Source Image detection out there! Recognizing the object and getting the vibe and aesthetic at the same time!

### Character Text Edit and Deletion
- Yes! You can edit your character's response like it's SillyTavern
- Yes! You can delete your character's response!
- No! You cannot regenerate character's response, I should really add that feature

### Pseudo Large Action Model Tech Demo!!!
- Uses GBNF Scripting to let the AI understand simple commmand.
- Sample command included in lam.py.
- Use > at the beginning your message (while also mentioning a bot's name) to trigger the LAM
- There's not many feature since it was only implemented a few hours ago...
- Honestly not a feature,  more like a neat little trick the AI can do..
- (This is partly another joke about Rabbit R1)
- ((All available commands are written in lam.py))
- (((Grammar Creation still required when adding new commmand)))
- ((((Character need to be told about the command thing in their definition to properly use it))))
- (((((Remind me to add proper intergration, this is still barebones)))))

### Stable Multi-line Support
- Uses some epic prompt enginneering to keep the AI stable (not that epic actually)
- If character is made in the correct format, the AI shouldn't hallucinate much outside of their character
- That's all~

## Prerequisites

### Large Language Model
If you want to be cultured, you'll also need to download one of these bad boys~

- [Stheno - One of the best Llama 8B Model](https://huggingface.co/Lewdiculous/L3-8B-Stheno-v3.1-GGUF-IQ-Imatrix) <- The Most Stable One Yet
- [Anjir - Top Performer in Chaiverse Leaderboard](https://huggingface.co/Hastagaras/Anjir-8B-L3?not-for-all-audiences=true) <- Ranked High On Chaiverse
- [Nyanade - One of the best Llama 7B Model](https://huggingface.co/Lewdiculous/Nyanade_Stunna-Maid-7B-v0.2-GGUF-IQ-Imatrix) <- 7B Model, Use At Your Own Risk

### Koboldcpp
Requires Koboldcpp for back end, download it here:
[Koboldcpp](https://github.com/LostRuins/koboldcpp)

### Florence 2

- Microsoft New Visual AI
- Decent, ish
- By default this AI will use both Florence and Llava embedding at the same time
- Florence for Object Recognition and OCR
- Llava for Image Vibe Detection
 
### Additional configuration needed to run the bot
- Discord API key in .env in the global variable
- make new character json files in the characters folder
- Or just, yknow, make lots and lots of character json file!!! Refer to characters/default.json for example


## Instructions:

To run this bot:

1. Load the LLM model of your choice in Koboldcpp (Make sure it's marked as not safe for audience)
2. Download this repository ~~[OpenKlyde](https://github.com/badgids/OpenKlyde)~~ [DiscordBot](https://github.com/Ambruk-chan/DiscordBot)
3. Make a .env file as written in example.env
4. Install the requirements. I suggest using an Anaconda or Miniconda instance.
    ```pip install -r requirements.txt```
5. Run the bot with `python bot.py`

## Character creation

Refer to README.md file in the characters folder.

## ToDo (From Top Priority to the Least Important):

- [x] Make a better README.
- [x] Add Webhook Support for more seamless Avatar Change
- [x] Fixed the Webhook not detecting reply, (hopefully I don't get rate limited)
- [x] Refactor this whole entire mess...
- [x] Redo the character trigger and swapping system with webhook.
- [x] Implement GBNF for literal fucking Large Action Model feature.
- [ ] Add a nicer way to add the Large Action Model Feature

## Known Issue:
- Cannot Reply In Thread
  - Skill Issue on my part, will figure it out later
- Terrible Documentation
  - As in like, I did not make any proper Github Commit Comment :v
  - Honestly this whole thing started as a joke, if you see the Read Me file, it's all just irony
  - I never expected it to work this well

Yeah that's all the current issue. Let me know if there's another one, have fun then~
