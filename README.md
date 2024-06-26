Aktiva AI - A Self Hosted AI Discord Bot

Big thank you to @badgids for making this possible, hehe~

## Prerequisites

Download Koboldcpp here:
[Koboldcpp](https://github.com/LostRuins/koboldcpp)

If you want to be cultured, you'll also need to download one of these bad boys~

- [Stheno - One of the best Llama 8B Model](https://huggingface.co/Lewdiculous/L3-8B-Stheno-v3.1-GGUF-IQ-Imatrix) 
- [Anjir - Top Performer in Chaiverse Leaderboard](https://huggingface.co/Hastagaras/Anjir-8B-L3?not-for-all-audiences=true)
- [Nyanade - One of the best Llama 7B Model](https://huggingface.co/Lewdiculous/Nyanade_Stunna-Maid-7B-v0.2-GGUF-IQ-Imatrix)


### Stable Diffusion
~~- bot supports stable diffusion but I recommend using SDXL as the bot will send a prompt to SD in natural language and previous SD (like SD1.5) would struggle~~

Still a work in progress, but I will definitely not be sending prompt to SD in Natural Language! 

Cuz I got GBNF, take that corpo garbage!!!

### Koboldcpp, OpenAI API, Mistral API
- The bot supports koboldcpp API
- ~~but also OpenAI-compatible backends. Look in configurations folder for examples. Put your API key in the~~ ~~'Bearer' line~~ Ahaha! No, never.
### Additional configuration needed to run the bot
- Discord API key in .env in the global variable
- make new character json files in the characters folder
- Or just, yknow, make lots and lots of character json file!!! Refer to characters/default.json for example
- Character Kisna originally made by Bronya Rand


## Instructions:

To run this bot:

1. Load the LLM model of your choice in Koboldcpp (Make sure it's marked as not safe for audience)
2. Download this repository ~~[OpenKlyde](https://github.com/badgids/OpenKlyde)~~ [DiscordBot](https://github.com/Ambruk-chan/DiscordBot)
3. Make a .env file as written in example.env
4. Install the requirements. I suggest using an Anaconda or Miniconda instance.
    ```pip install -r requirements.txt```
5. I might have messed up with the requirements.txt, but I think you also need to download and install tesseract.
6. Run the bot with `python bot.py`

Cheers!

## ToDo (From Top Priority to the Least Important):

- [x] Make a better README.
- [x] Add Webhook Support for more seamless Avatar Change
- [x] Fixed the Webhook not detecting reply, (hopefully I don't get rate limited)
- [x] Refactor this whole entire mess...
- [x] Redo the character trigger and swapping system with webhook.
- [ ] Implement GBNF for literal fucking Large Action Model feature.
- [ ] Enable support for ~~Character.ai~~, TavernAI, SillyTavern, etc. character formats. (currently not practical)
- [ ] Make User Friendly UI to set things up.

## Known Issue:
- Character Memory 
  - There's no easy way to tweak what character remembers (FIXED)
  - Character has a separate memory for each user (FIXED)
  - Character can't see the content of the channel (FIXED)
- Cannot Reply In Thread
  - Skill Issue on my part, will figure it out later
- No Slash Command
  - Not necessarily an issue, but all setup happens in the code, I want to add more slash command to change stuff like API Access, System Prompt, Editing Character Definition, Making New Character, and such. 
- Terrible Documentation
  - As in like, I did not make any proper Github Commit Comment :v
  - Honestly this whole thing started as a joke, if you see the Read Me file, it's all just irony
  - I never expected it to work this well
- System Prompt
  - System Prompt is just awful, the instruction sent to the AI is still designed for RP and not Discord Chat (FIXED)
  - Excessive use of Emoji, Kaomoji, and all that stuff (FIXED)

Yeah that's all the current issue.
