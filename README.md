# text-adventure-line-bot
Final project for Theory of Computation, build a Line bot that runs a text adventure game with state machines
# Tools, Packages
- Django
- Pytransitions Package(python)
- Line Bot SDK
- PythonAnywhere(for deploying)
- Line Developer Console
# Basic Requirements
## FSM
Whole State Diagram
![](./text_adventure_line_bot/static/whole_state_diagram.png)

Initial State Diagram
![](./text_adventure_line_bot/static/initial_state_diagram.png)

Implemented with pytransitions/transitions package
## Line Bot
- Made With Django and Line Bot SDK
- Deployed on [PythonAnywhere](https://www.pythonanywhere.com)
## Files
- [README.md](README.md)
- [state diagrams in static directory](./text_adventure_line_bot/static/)
## How to use
1. Scan QR code with your phone, or search Line ID:@899djtxa 
<img src='./text_adventure_line_bot/static/qr_code.png' width='100' alt='QR CODE'/>
2. Add the bot as friend
3. The bot will tell you the story and offer you options, you can press buttons on screen or type uppercase letters to act

<img src='./text_adventure_line_bot/static/in_game_image.jpg' height='400' alt='game screen'/>

4. Try to find out all 5 endings and easter eggs