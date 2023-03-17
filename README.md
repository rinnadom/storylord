# StoryLord: Children's Book Generator

# Example
```
from storylord import StoryLord

story_prompt = "A turtle journeys into outer space to find signs of extraterrestrial life"
    
lord = StoryLord()
lord.create_storybook(story_prompt)
```

# Requirements
OpenAI API Key needs to be provided to `StoryLord` as an kwarg, or set an env. variable.