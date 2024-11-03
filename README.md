**Libraries required:**
  - python_telegram_bot

**Languages supported**:
  - Russian
  - English

**What does this bot do**:
  The bot tries to guess an animal (after a couple of small correction it could be absolutely anything) based on its characteristics. To do it, it follows the tree. 
  Each layer is made of 3 parts: 
    the characteristic, 
    the branch if the characteristic belongs to the animal,
    the branch if the characteristic if false.
  The bot navigates by the tree choosing one branch or another.
  If a characteristic or an animal is not in the tree a player can add it there.
