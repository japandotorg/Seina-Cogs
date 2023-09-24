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

from typing import Final, List

__all__ = ("SWORDS", "PROMPTS", "WINNER_PROMPTS")


SWORDS: Final[str] = "https://cdn.discordapp.com/emojis/1123588896136106074.webp"


PROMPTS: List[str] = [
    "{killed} was killed by {killer}.",
    "{killer} killed {killed} with an axe 🪓!",
    "{killer} slaughtered {killed} with their looks 😎.",
    "{killer} murdered {killed}.",
    "{killer} beat {killed} to death with a rainbow trout 🐟.",
    "{killer} sucked the life out of {killed}.",
    "{killer} ran over {killed} with a taco 🌮 truck.",
    "{killer} drove {killed} to the point of insanity 🤯.",
    "{killer} ran {killed} over with a truck 🚚.",
    "{killer} lit {killed}'s hair on fire 🔥!",
    "{killer} fed {killed} to a bear 🐻!",
    "{killed} died of food poisoning 🤮 from {killer}'s cooking 🍲.",
    "{killed} was pushed in front of a train by 🚄 {killer}!",
    "{killer}'s snake 🐍 bit {killed} in the eye 👁️.",
    "{killer} I Tell You One Thing, I'm Getting Too Old For This Nonsense. {killed} was shoot!🔫",
    "{killer} killed {killed} with a knife 🔪!",
    "{killed} You were killed by an exploding vehicle. Vehicles on fire are likely to explode.",
    "{killed} You were killed by a vehicle explosion 🔥.",
    "{killed} You were killed by a moving vehicle driven by {killer}.🚗",
    "{killer} killed {killed} with a grenade 🧨!",
    "{killer} killed {killed} with a rocket launcher 🚀!",
    "{killer} killed {killed} with a shotgun 🤠!",
    "{killer} ran over {killed} with a car 🚗!",
    "There is no escape from {killer}! {killed} was killed by a headshot 🎯!",
    "{killer} set fire to kill {killed} with a Molotov Cocktail 🔥!",
    "{killer} sniped {killed} from 300 meters away 🎯!",
    "{killer} killed {killed} with a pistol 🔫!",
    "{killer} killed {killed} with a rifle 🎯!",
    "{killer} killed {killed} with a submachine gun 🔫!",
    "{killer} killed {killed} with a machine gun 🔫!",
    "{killer} killed {killed} with a sword 🗡️!",
    "{killer} killed {killed} with a spear 🪓!",
    "{killer} killed {killed} with a hammer 🔨!",
    "{killer} killed {killed} with a baseball bat ⚾!",
    "{killer} killed {killed} with a hockey stick 🏒!",
    "{killer} killed {killed} with a pool cue 🎱!",
    "{killer} killed {killed} with a cricket bat 🏏!",
    "{killer} killed {killed} with a shovel 🪓!",
    "{killer} killed {killed} with a pickaxe ⛏️!",
    "{killed} met their demise at the hands of {killer}. 💀",
    "{killer} obliterated {killed} with a powerful spell ✨!",
    "{killer} outsmarted {killed} and took them down. 🎯",
    "{killer} unleashed their fury upon {killed} and ended their life. 😡",
    "{killer} struck down {killed} with lightning speed ⚡!",
    "{killed} met their demise at the hands of {killer}.",
    "{killer} terminated {killed} with extreme prejudice.",
    "{killer} dispatched {killed} without mercy.",
    "{killer} brought about the demise of {killed}.",
    "{killer} extinguished {killed}'s life force.",
    "{killer} wiped out {killed} from the face of the Earth.",
    "{killed} met their untimely end due to {killer}'s actions.",
    "{killed} perished under the hand of {killer}.",
    "{killer} pulled the trigger, ended {killed}'s life",
    "{killer} obliterated {killed} without hesitation.",
    "{killer} inflicted a fatal blow upon {killed}.",
    "{killed} succumbed to {killer}'s murderous ways.",
    "{killed} fell victim to {killer}'s deadly plot.",
    "{killer} brought about the demise of {killed} with precision.",
    "{killer} enacted a deadly scheme that ended {killed}'s life.",
    "{killed}'s life was claimed by the cold grip of {killer}",
    "{killer} sent {killer} to their eternal rest.",
    "{killer} left no trace of {killed}'s existence.",
    "{killed} met a horrifying end at the hands of {killer}.",
    "{killer} unleashed unspeakable terror upon {killed}.",
    "{killer} plunged {killed} into a world of eternal darkness.",
    "{killed} became a mere puppet in {killer}'s twisted game of death.",
    "{killer} revealed in the screams of agony as they extinguished {killed}'s life.",
    "{killer} casted {killed} into a realm of overlasting torment and despair.",
    "{killer} painted a macabre masterpiece with {killed}'s lifeblood as their brush.",
    "{killer} unleashed a cataclysmic force upon {killed}, obliterating all hope.",
    "{killed} was consumed by the fiery wrath of {killer}.",
    "{killer} carved a path of devastation, leaving {killed} in ruins.",
    "{killer} tore through {killed} with savage ferocity, leaving a trail of devastation in their wake.",
    "{killer} descended upon {killed} with ferocious intent, their wrath leaving a trail of devastation in its wake.",
    "{killer} was caught in a deadly dance with {killer}, their fate sealed with each lethal movement.",
    "{killed} encountered {killer} in a battle of wills, their struggle culminating in a cataclysmic clash of life and death.",
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
