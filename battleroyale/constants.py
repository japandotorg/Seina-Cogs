"""
MIT License

Copyright (c) 2023-present japandotorg

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from typing import Final, List, Tuple

import discord

__all__: Tuple[str, ...] = (
    "MAX_LEVEL",
    "MIN_EXP",
    "MAX_EXP",
    "EXP_MULTIPLIER",
    "STARTING_EXP",
    "SWORDS",
    "PROMPTS",
    "WINNER_PROMPTS",
)


MAX_LEVEL: Final[int] = 100


MIN_EXP: Final[int] = 10
MAX_EXP: Final[int] = 100


EXP_MULTIPLIER: Final[int] = 15
STARTING_EXP: Final[int] = 10_00


SWORDS: Final[str] = "https://cdn.discordapp.com/emojis/1123588896136106074.webp"


EMOJIS: List[discord.PartialEmoji] = [
    discord.PartialEmoji.from_str("😈"),
    discord.PartialEmoji.from_str("💀"),
    discord.PartialEmoji.from_str("🤬"),
    discord.PartialEmoji.from_str("🔪"),
    discord.PartialEmoji.from_str("😤"),
]


PROMPTS: List[str] = [
    "{emoji} | {killed} was killed by {killer}.",
    "{emoji} | {killer} killed {killed} with an axe 🪓!",
    "{emoji} | {killer} slaughtered {killed} with their looks 😎.",
    "{emoji} | {killer} murdered {killed}.",
    "{emoji} | {killer} beat {killed} to death with a rainbow trout 🐟.",
    "{emoji} | {killer} sucked the life out of {killed}.",
    "{emoji} | {killer} ran over {killed} with a taco 🌮 truck.",
    "{emoji} | {killer} drove {killed} to the point of insanity 🤯.",
    "{emoji} | {killer} ran {killed} over with a truck 🚚.",
    "{emoji} | {killer} lit {killed}'s hair on fire 🔥!",
    "{emoji} | {killer} fed {killed} to a bear 🐻!",
    "{emoji} | {killed} died of food poisoning 🤮 from {killer}'s cooking 🍲.",
    "{emoji} | {killed} was pushed in front of a train by 🚄 {killer}!",
    "{emoji} | {killer}'s snake 🐍 bit {killed} in the eye 👁️.",
    "{emoji} | {killer} I Tell You One Thing, I'm Getting Too Old For This Nonsense. {killed} was shoot!🔫",
    "{emoji} | {killer} killed {killed} with a knife 🔪!",
    "{emoji} | {killed} You were killed by an exploding vehicle. Vehicles on fire are likely to explode.",
    "{emoji} | {killed} You were killed by a vehicle explosion 🔥.",
    "{emoji} | {killed} You were killed by a moving vehicle driven by {killer}.🚗",
    "{emoji} | {killer} killed {killed} with a grenade 🧨!",
    "{emoji} | {killer} killed {killed} with a rocket launcher 🚀!",
    "{emoji} | {killer} killed {killed} with a shotgun 🤠!",
    "{emoji} | {killer} ran over {killed} with a car 🚗!",
    "{emoji} | There is no escape from {killer}! {killed} was killed by a headshot 🎯!",
    "{emoji} | {killer} set fire to kill {killed} with a Molotov Cocktail 🔥!",
    "{emoji} | {killer} sniped {killed} from 300 meters away 🎯!",
    "{emoji} | {killer} killed {killed} with a pistol 🔫!",
    "{emoji} | {killer} killed {killed} with a rifle 🎯!",
    "{emoji} | {killer} killed {killed} with a submachine gun 🔫!",
    "{emoji} | {killer} killed {killed} with a machine gun 🔫!",
    "{emoji} | {killer} killed {killed} with a sword 🗡️!",
    "{emoji} | {killer} killed {killed} with a spear 🪓!",
    "{emoji} | {killer} killed {killed} with a hammer 🔨!",
    "{emoji} | {killer} killed {killed} with a baseball bat ⚾!",
    "{emoji} | {killer} killed {killed} with a hockey stick 🏒!",
    "{emoji} | {killer} killed {killed} with a pool cue 🎱!",
    "{emoji} | {killer} killed {killed} with a cricket bat 🏏!",
    "{emoji} | {killer} killed {killed} with a shovel 🪓!",
    "{emoji} | {killer} killed {killed} with a pickaxe ⛏️!",
    "{emoji} | {killed} met their demise at the hands of {killer}. 💀",
    "{emoji} | {killer} obliterated {killed} with a powerful spell ✨!",
    "{emoji} | {killer} outsmarted {killed} and took them down. 🎯",
    "{emoji} | {killer} unleashed their fury upon {killed} and ended their life. 😡",
    "{emoji} | {killer} struck down {killed} with lightning speed ⚡!",
    "{emoji} | {killed} met their demise at the hands of {killer}.",
    "{emoji} | {killer} terminated {killed} with extreme prejudice.",
    "{emoji} | {killer} dispatched {killed} without mercy.",
    "{emoji} | {killer} brought about the demise of {killed}.",
    "{emoji} | {killer} extinguished {killed}'s life force.",
    "{emoji} | {killer} wiped out {killed} from the face of the Earth.",
    "{emoji} | {killed} met their untimely end due to {killer}'s actions.",
    "{emoji} | {killed} perished under the hand of {killer}.",
    "{emoji} | {killer} pulled the trigger, ended {killed}'s life",
    "{emoji} | {killer} obliterated {killed} without hesitation.",
    "{emoji} | {killer} inflicted a fatal blow upon {killed}.",
    "{emoji} | {killed} succumbed to {killer}'s murderous ways.",
    "{emoji} | {killed} fell victim to {killer}'s deadly plot.",
    "{emoji} | {killer} brought about the demise of {killed} with precision.",
    "{emoji} | {killer} enacted a deadly scheme that ended {killed}'s life.",
    "{emoji} | {killed}'s life was claimed by the cold grip of {killer}",
    "{emoji} | {killer} sent {killed} to their eternal rest.",
    "{emoji} | {killer} left no trace of {killed}'s existence.",
    "{emoji} | {killed} met a horrifying end at the hands of {killer}.",
    "{emoji} | {killer} unleashed unspeakable terror upon {killed}.",
    "{emoji} | {killer} plunged {killed} into a world of eternal darkness.",
    "{emoji} | {killed} became a mere puppet in {killer}'s twisted game of death.",
    "{emoji} | {killer} revealed in the screams of agony as they extinguished {killed}'s life.",
    "{emoji} | {killer} casted {killed} into a realm of overlasting torment and despair.",
    "{emoji} | {killer} painted a macabre masterpiece with {killed}'s lifeblood as their brush.",
    "{emoji} | {killer} unleashed a cataclysmic force upon {killed}, obliterating all hope.",
    "{emoji} | {killed} was consumed by the fiery wrath of {killer}.",
    "{emoji} | {killer} carved a path of devastation, leaving {killed} in ruins.",
    "{emoji} | {killer} tore through {killed} with savage ferocity, leaving a trail of devastation in their wake.",
    "{emoji} | {killer} descended upon {killed} with ferocious intent, their wrath leaving a trail of devastation in its wake.",
    "{emoji} | {killer} was caught in a deadly dance with {killer}, their fate sealed with each lethal movement.",
    "{emoji} | {killed} encountered {killer} in a battle of wills, their struggle culminating in a cataclysmic clash of life and death.",
]


WINNER_PROMPTS: List[str] = [
    "{winner} is the winner 🏆!",
    "Winner winner, chicken 🐔 dinner! Congrats {winner}!",
    "Heyyyyoooo, {winner} won 🏆!",
    "In the end... {winner} was all that remained.",
    "{winner} is your final survivor.",
    "We have a winner and it's.. {winner}, You'll Walk... With A Limp!",
    "Its not about winning and losing. You know who says that? The loser. {winner} is the winner!",
    "{winner} didnt lose the game, they just ran out of time and took down everyone!",
    "Winning and losing does not have any meaning, because some people win by losing and some lose by winning. {winner} Congratulations of winning!",
    "{winner} You never lose, you either win or you learn.",
    "Winning is not everything, but the effort to win is. {winner} You did it!",
    "You freaking did it {winner}! You won!",
    "You are the winner {winner}! You are the best!",
    "Ayoo {winner}, Victory has a hundred fathers, but defeat is an orphan.",
    "Yesterday I dared to struggle. Today I dare to win and you did it {winner}!",
    "Why do I win every time? {winner} Because I'm the best, and everyone else sucks.",
    "You are a winner {winner}! You are just a winner i swear, congrats!🏆",
    "For every winner, there are dozens of losers. Odds are you're one of them {winner}!",
    "You shouldn't focus on why you can't win, and you should focus on the winner, {winner}!",
    "Why are you so good {winner}? I'm just a winner, I guess.",
]
