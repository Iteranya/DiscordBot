# ~~OpenKlyde~~ Ambruk-chan - A Self Hosted AI Discord Bot

Big thank you to @badgids for making this possible, hehe~

No, no, nothing weird with this fork. Just a little bit of improvement here and there. A little bit of this, a little bit of that, nothing weird at all~ 

## Prerequisites

Download Koboldcpp here:
[Koboldcpp](https://github.com/LostRuins/koboldcpp)

If you want to be cultured, you'll also need to download one of these bad boys~

- [Stheno](https://huggingface.co/Lewdiculous/L3-8B-Stheno-v3.1-GGUF-IQ-Imatrix) 
- [Anjir](https://huggingface.co/Hastagaras/Anjir-8B-L3?not-for-all-audiences=true)
- [Nyanade](https://huggingface.co/Lewdiculous/Nyanade_Stunna-Maid-7B-v0.2-GGUF-IQ-Imatrix)

----NEW----:

~~XTTS support added thanks to [Elbios](https://github.com/Elbios)'s hard work and changes in their fork!~~

Nonsense! I don't need XTTS to speak with all of you! 
Unless... You want me to make an ASMR? Muehehe~

### Stable Diffusion
~~- bot supports stable diffusion but I recommend using SDXL as the bot will send a prompt to SD in natural language and previous SD (like SD1.5) would struggle~~

Still a work in progress, but I will definitely not be sending prompt to SD in Natural Language! 

Cuz I got GBNF, take that corpo garbage!!!

### Koboldcpp, OpenAI API, Mistral API
- The bot supports koboldcpp API ~~but also OpenAI-compatible backends. Look in configurations folder for examples. Put your API key in the~~ ~~'Bearer' line~~ ClosedAI, Anthropic, and Google can \[REDACTED\] MY \[DATA EXPUNGED\] and \[CENSORED\] you hear me?! \[EXPLICITIVES REMOVED\]YA'LL!!!

### Additional configuration needed to run the bot
- Discord API key in bot.py in the global variable
~~- If using openai/mistral - API key in Bearer line in configuration/text-default.json~~
- fill in characters/default.json with your character prompt
- optionally in functions.py in function get_character() you can fill out the 'examples' array with examples of dialogue you want the bot to follow


## Instructions:

To run this bot:

1. Load the LLM model of your choice in Koboldcpp (Make sure it's marked as not safe for audience)
2. Download this repository ~~[OpenKlyde](https://github.com/badgids/OpenKlyde)~~ [DiscordBot](https://github.com/Ambruk-chan/DiscordBot)
3. Open bot.py and at replace API_KEY with your bot's API key
4. Install the requirements. I suggest using an Anaconda or Miniconda instance.
    ```pip install -r requirements.txt```
5. Run the bot with `python bot.py`
   ~~- optionally with --tts_xtts flag~~

Cheers!

## ToDo (From Top Priority to the Least Important):

- [x] Make a better README.
- [x] Add Webhook Support for more seamless Avatar Change
- [x] Fixed the Webhook not detecting reply, (hopefully I don't get rate limited)
- [x] Refactor this whole entire mess...
- [x] Redo the character trigger and swapping system with webhook.
- [ ] Implement GBNF for literal fucking Large Action Model feature.
- [ ] Add more standard Discord Bot features. (music, games, moderation, etc.)
- [ ] Enable support for ~~Character.ai~~, TavernAI, SillyTavern, etc. character formats. (currently not practical)
- [ ] Make User Friendly UI to set shit up.

## Known Issue:
- Character Memory 
  - There's no easy way to tweak what character remembers (obviously, the interface is Discord)
  - Character has a separate memory for each user (So like, it's similar to a DM with a group of AI)
  - Character can't see the content of the channel (I'm planning to add the 'AI Channel' feature where you can have a channel that is being logged by the bot and everything in the history of it is visible to the AI... If possible)
- Cannot Reply In Thread
  - Skill Issue on my part, will figure it out later
- No Slash Command
  - Not necessarily an issue, but all setup happens in the code, I want to add more slash command to change stuff like API Access, System Prompt, Editing Character Definition, Making New Character, and such. 
- Terrible Documentation
  - As in like, I did not make any proper Github Commit Comment :v
  - Honestly this whole thing started as a joke, if you see the Read Me file, it's all just irony
  - I never expected it to work this well
- System Prompt
  - System Prompt is just awful, the instruction sent to the AI is still designed for RP and not Discord Chat
  - Excessive use of Emoji, Kaomoji, and all that stuff

Yeah that's all the current issue.
